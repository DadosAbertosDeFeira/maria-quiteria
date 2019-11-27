import scrapy
from scrapy import Request


class GazetteSpider(scrapy.Spider):
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
                url = self.build_url(url, next_page)

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

    def build_url(self, url, next_page):
        # FIXME duplicated method - find a better approach
        page_index = url.find('&p=') + 3
        end_page_index = url[page_index:].find('&')
        prefix = url[:page_index]
        params = url[page_index:][end_page_index:]
        return f'{prefix}{next_page}{params}'
