import re

import scrapy
from scrapy import Request

from .utils import replace_query_param


class LegacyGazetteSpider(scrapy.Spider):
    """Coleta diário oficial de Feira de Santana até 2015.

    Years: 1999 to 2015
    Example: http://www.feiradesantana.ba.gov.br/seadm/leis.asp?acao=ir&p=24&ano=2015
    """
    name = 'legacy_gazette'
    start_urls = [
        f'http://www.feiradesantana.ba.gov.br/servicos.asp?'
        f'acao=ir&s=a&link=seadm/leis.asp&p=1&'
        f'txtlei=%27Pesquisar%20pelo%20n%FAmero%20do%20ato%20ou%20palavra-chave%27'
        f'&cat=0'
        f'&ano={year}#links'
        for year in range(1999, 2016)
    ]

    def parse(self, response):
        """
        @url http://www.feiradesantana.ba.gov.br/servicos.asp?acao=ir&s=a&link=seadm/leis.asp&p=1&cat=0&ano=2001#links
        @returns items 8 13
        @returns requests 1 2
        """
        if 'SEM INFORMA' not in response.text:  # it means page found
            rows = response.css('table tr td table tr td table tr td table tr td.txt')
            for row in rows:
                act = self.extract_acts(row)
                yield {
                    'title': act['act_and_date'],
                    'published_on': act['journal'],
                    'date': act['date'],
                    'details': act['details'],
                    'url': act['url'],
                    'source': response.url,
                }

            current_page = self.get_current_page(response)
            last_page = response.xpath('//table/tr[10]/td/ul/li/a/text()')

            if current_page and last_page:
                last_page = int(last_page[-1].get().strip())
                next_page = int(current_page.strip()) + 1

                if next_page <= last_page:
                    url = replace_query_param(response.url, 'p', next_page)
                    yield response.follow(url, callback=self.parse)
        else:
            self.logger.info(f'End of pages')

    def get_current_page(self, response):
        current_page = response.xpath(
            "//table/tr[10]/td/ul/li[contains(@class, 'current')]/a/text()"
        ).get()
        if current_page is None:
            current_page = response.css('li.current ::text').get()
        if current_page is None:
            current_page = response.css('ul.pagination li.active ::text').get()
        return current_page

    def extract_acts(self, row):
        text = row.xpath('span/strong/text()').extract()
        act = {
            'url': row.xpath('a//@href').extract_first(),
            'act_and_date': text[0],
            'details': row.xpath('a//text()').extract_first(),
            'journal': '',
            'date': ''
        }
        if len(text) > 1:
            journal_label = text[1]  # Jornal Publicado:
            date_label = text[2]  # Data:

            whole_text = ''.join([
                chunk.strip().replace('-', '')
                for chunk in row.css('::text').extract()
            ])

            whole_text = whole_text \
                .replace(text[0], '') \
                .replace(act['details'], '') \
                .replace(journal_label, '')
            date_index = whole_text.rfind(date_label)
            act['journal'] = whole_text[:date_index].strip()
            act['date'] = whole_text[date_index + len(date_label):]

        return act


class GazetteExecutiveAndLegislativeSpider(scrapy.Spider):
    """Coleta o Diário Oficial dos poderes executivo e legislativo."""
    name = 'gazettes'
    allowed_domains = ['diariooficial.feiradesantana.ba.gov.br']
    start_urls = ['http://www.diariooficial.feiradesantana.ba.gov.br']
    powers = {'executivo': 1, 'legislativo': 2}
    last_page = 1
    handle_httpstatus_list = [302]

    def parse(self, response):
        gazette_table = response.css('.style166')
        gazettes_links = gazette_table.xpath('a//@href').extract()
        dates = gazette_table.css('a::text').extract()

        for url, date in zip(gazettes_links, dates):
            edition = self.extract_edition(url)
            power = self.extract_power(url)
            power_id = self.powers[power]

            gazette = dict(
                date=date,
                power=power,
                url=response.urljoin(url),
                file_url=response.urljoin(f'abrir.asp?edi={edition}&p={power_id}')
            )

            yield Request(
                gazette['url'],
                callback=self.parse_details,
                meta={'gazette': gazette}
            )

        current_page_selector = '#pages ul li.current::text'
        current_page = response.css(current_page_selector).extract_first()
        next_page = int(current_page) + 1
        next_page_url = response.urljoin(f'/?p={next_page}')

        if next_page > self.last_page:
            self.last_page = next_page
            yield Request(next_page_url)

    def parse_details(self, response):
        gazette = response.meta['gazette']

        gazette['edition'] = response.css('span.style4 ::text').extract()[1].strip()
        titles = response.xpath("//tr/td/table/tr/td[@colspan='2']/text()").extract()
        descriptions = response.css('td.destaqt ::text').extract()

        topics = []
        while titles:
            topics.append({
                'title': titles.pop(0).strip(),
                'agency': descriptions.pop(0).strip(),
                'topic': descriptions.pop(0).strip()
            })
            titles.pop(0)

        if gazette.get('topics') is None:
            gazette['topics'] = topics
        else:
            gazette['topics'].extend(topics.copy())

        current_page = response.css('ul li.current ::text').extract_first()
        last_page = response.css('ul li:last-child ::text').extract_first()
        if current_page:
            current_page = current_page.strip()
            last_page = last_page.strip()
            if current_page != last_page:
                next_page = int(current_page) + 1
                url = response.css('ul li a::attr(href)').extract_first()
                url = replace_query_param(url, 'p', next_page)

                yield Request(
                    response.urljoin(url),
                    callback=self.parse_details,
                    meta={'gazette': gazette}
                )
            else:
                yield Request(
                    gazette['file_url'],
                    callback=self.parse_document_url,
                    meta={'gazette': gazette}
                )

    def parse_document_url(self, response):
        gazette = response.meta['gazette']
        url = response.headers['Location'].decode('utf-8')
        gazette['file_urls'] = [url.replace('https', 'http')]
        return gazette

    def extract_power(self, url):
        if url.find('st=1') != -1:
            return 'executivo'
        return 'legislativo'

    def extract_edition(self, url):
        edition_index = url.find('edicao=') + len('edicao=')
        edition = url[edition_index:]
        return edition
