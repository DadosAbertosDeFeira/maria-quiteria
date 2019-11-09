import re
import scrapy


class Laws(scrapy.Spider):
    """Parse laws and acts of Feira de Santana city hall until 2015.

    Years: 1999 to 2015
    Example: http://www.feiradesantana.ba.gov.br/seadm/leis.asp?acao=ir&p=24&ano=2015
    """
    name = 'laws'
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
        if 'SEM INFORMA' not in response.text:  # page found
            rows = response.css('table tr td table tr td table tr td table tr td.txt')
            for row in rows:
                act_url = row.xpath('a//@href').extract_first()
                change = row.xpath('a//text()').extract_first()
                text = row.xpath('span/strong/text()').extract()
                act_and_date = text[0]
                if len(text) > 1:
                    journal_label = text[1]  # Jornal Publicado:
                    date = text[2]  # Data:

                    whole_text = ''.join([
                        chunk.strip().replace('-', '')
                        for chunk in row.css('::text').extract()
                    ])

                    whole_text = whole_text \
                        .replace(text[0], '') \
                        .replace(change, '') \
                        .replace(journal_label, '')
                    date_index = whole_text.rfind(date)
                    journal = whole_text[:date_index].strip()
                    date = whole_text[date_index + len(date):]
                else:
                    journal = ''
                    date = ''

                yield {
                    'titulo': act_and_date,
                    'jornal_publicado': journal,
                    'data': date,
                    'detalhes': change,
                    'url': act_url,
                    'fonte': response.url,
                }

            last_page = response.xpath('//table/tr[10]/td/ul/li/a/text()')
            current_page = response.xpath("//table/tr[10]/td/ul/li[contains(@class, 'current')]/a/text()").get()
            if current_page is None:
                current_page = response.css('li.current ::text').get()
            if current_page is None:
                current_page = response.css('ul.pagination li.active ::text').get()

            if current_page and last_page:
                last_page = last_page[-1].get()
                last_page = int(last_page.strip())
                current_page = int(current_page.strip())
                next_page = int(current_page) + 1

                self.logger.info(f'=============================== next page {next_page}')

                if next_page <= last_page:
                    page_index = response.url.find('&p=') + 3
                    end_page_index = response.url[page_index:].find('&')
                    before_page = response.url[:page_index]
                    after_page = response.url[page_index:][end_page_index:]

                    url = f'{before_page}{next_page}{after_page}'
                    yield response.follow(url, callback=self.parse)
        else:
            self.logger.info(f'=============================== not found')


class BidsSpider(scrapy.Spider):
    name = 'bids'
    start_urls = ['http://www.feiradesantana.ba.gov.br/seadm/licitacoes.asp']
    bid_id = 0

    def parse(self, response):
        """
        @url http://www.feiradesantana.ba.gov.br/seadm/licitacoes.asp
        @returns items 0
        @returns requests 166
        """
        all_bidding_urls = response.xpath('//table/tbody/tr/td[1]/div/a//@href').extract()
        base_url = 'http://www.feiradesantana.ba.gov.br'

        for url in all_bidding_urls:
            if base_url not in url:
                # all years except 2017 and 2018
                url = f'{base_url}/seadm/{url}'
            yield response.follow(url, self.parse_page)

    def parse_page(self, response):
        raw_modalities = response.xpath('//tr/td[1]/table/tr/td/text()').extract()
        raw_descriptions = response.xpath(
            '//table/tr[2]/td/table/tr[6]/td/table/tr/td[2]/table[1]'
        )
        raw_bids_history = response.xpath(
            '//table/tr[2]/td/table/tr[6]/td/table/tr/td[2]/table[2]'
        )
        raw_when = response.xpath('//tr/td[3]/table/tr/td/text()').extract()
        descriptions = self._parse_descriptions(raw_descriptions)
        bids_history = self._parse_bids_history(raw_bids_history)
        modalities = self._parse_modalities(raw_modalities)
        when = self._parse_when(raw_when)

        for modality, (description, document_url), bid_history, when in zip(
            modalities, descriptions, bids_history, when
        ):
            url_pattern = re.compile(r'licitacoes_pm\.asp[\?|&]cat=(\w+)\&dt=(\d+-\d+)')
            match = url_pattern.search(response._url)
            month, year = match.group(2).split('-')

            yield {
                'id': self.bid_id,
                'url': response._url,
                'category': match.group(1).upper(),
                'month': int(month),
                'year': int(year),
                'description': description,
                'history': bid_history,
                'modality': modality,
                'when': when,
                'document_url': document_url,
            }

            self.bid_id += 1

    def _parse_descriptions(self, raw_descriptions):
        descriptions = []
        for raw_description in raw_descriptions:
            description = raw_description.xpath('.//text()').extract()
            document_url = raw_description.xpath('.//@href').extract_first()
            description = self._parse_description(description)

            if description != 'Objeto':
                document_url = document_url if document_url else ''
                descriptions.append((description, document_url))
        return descriptions

    def _parse_bids_history(self, raw_bids_history):
        all_bids_history = []
        for raw_bid_history in raw_bids_history:
            bids_history = []
            for row in raw_bid_history.xpath('.//tr'):
                when = row.xpath('.//td[2]/text()').get().strip()
                event = row.xpath('.//td[3]/div/text()').get()
                url = row.xpath('.//td[4]/div/a//@href').get()

                if event and when:
                    bids_history.append(
                        {'when': when, 'event': event.capitalize(), 'url': url if url else ''}
                    )
            all_bids_history.append(bids_history)

        return all_bids_history

    def _parse_description(self, raw_descriptions):
        descriptions = []
        for raw_description in raw_descriptions:
            description = raw_description.strip()
            if not description.isspace():
                descriptions.append(description)
        return ''.join(descriptions)

    def _parse_modalities(self, raw_modalities):
        modalities = []
        for raw_modality in raw_modalities:
            modality = raw_modality.strip()
            if modality != '':
                modality = modality.replace('\r\n', ' / ')
                modalities.append(modality)
        return modalities

    def _parse_when(self, raw_when):
        return [date[1:] for date in raw_when]
