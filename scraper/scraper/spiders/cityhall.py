import re
import scrapy


class LawsSpider(scrapy.Spider):
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
        if 'SEM INFORMA' not in response.text:  # it means page found
            rows = response.css('table tr td table tr td table tr td table tr td.txt')
            for row in rows:
                act = self.extract_acts(row)
                yield {
                    'titulo': act['act_and_date'],
                    'jornal_publicado': act['journal'],
                    'data': act['date'],
                    'detalhes': act['details'],
                    'url': act['url'],
                    'fonte': response.url,
                }

            current_page = self.get_current_page(response)
            last_page = response.xpath('//table/tr[10]/td/ul/li/a/text()')

            if current_page and last_page:
                last_page = int(last_page[-1].get().strip())
                next_page = int(current_page.strip()) + 1

                if next_page <= last_page:
                    url = self.build_url(response.url, next_page)
                    yield response.follow(url, callback=self.parse)
        else:
            self.logger.info(f'End of pages')

    def build_url(self, url, next_page):
        page_index = url.find('&p=') + 3
        end_page_index = url[page_index:].find('&')
        prefix = url[:page_index]
        params = url[page_index:][end_page_index:]
        return f'{prefix}{next_page}{params}'

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


class BidsSpider(scrapy.Spider):
    name = 'bids'
    start_urls = ['http://www.feiradesantana.ba.gov.br/seadm/licitacoes.asp']

    def parse(self, response):
        """
        @url http://www.feiradesantana.ba.gov.br/seadm/licitacoes.asp
        @returns items 0
        @returns requests 166
        """
        urls = response.xpath('//table/tbody/tr/td[1]/div/a//@href').extract()
        base_url = 'http://www.feiradesantana.ba.gov.br'

        for url in urls:
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
        bid_data = zip(modalities, descriptions, bids_history, when)

        url_pattern = re.compile(
            r'licitacoes_pm\.asp[\?|&]cat=(\w+)\&dt=(\d+-\d+)'
        )
        for modality, (description, document_url), history, when in bid_data:
            match = url_pattern.search(response._url)
            month, year = match.group(2).split('-')

            yield {
                'url': response._url,
                'category': match.group(1).upper(),
                'month': int(month),
                'year': int(year),
                'description': description,
                'history': history,
                'modality': modality,
                'when': when,
                'document_url': document_url,
            }

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
                    url = url if url else ''
                    bids_history.append({
                        'when': when,
                        'event': event.capitalize(),
                        'url': url
                    })
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


class ContractsSpider(scrapy.Spider):
    """Coleta contratos da página de contratos.

    http://www.transparencia.feiradesantana.ba.gov.br/index.php?view=contratos
    """
    name = 'contracts'
    url = 'http://www.transparencia.feiradesantana.ba.gov.br/controller/contrato.php'
    data = {
        'POST_PARAMETRO': 'PesquisaContratos',
        'POST_DATA': '',
        'POST_NMCREDOR': '',
        'POST_CPFCNPJ': '',
        'POST_NUCONTRATO': '',
    }

    def start_requests(self):
        return [scrapy.FormRequest(self.url, formdata=self.data, callback=self.parse)]

    def parse(self, response):
        # ['��� Anterior', '1', '2', '33', 'Pr��ximo ���']
        pages = response.css('div.pagination li a ::text').extract()
        last_page = int(pages[-2])

        for page in range(1, last_page + 1):
            data = self.data.copy()
            data['POST_PAGINA'] = str(page)
            data['POST_PAGINAS'] = str(last_page)
            yield scrapy.FormRequest(self.url, formdata=data, callback=self.parse_page)

    def parse_page(self, response):
        """Extract contracts from a page.

        Example:
        CONTRATO N° 11-2017-1926C   REFERENTE A CONTRATAÇÃO DE EMPRESA AQUISIÇÃO DE
        ÁGUA MINERAL NATURAL PARA A...
        OBJETO:REFERENTE A CONTRATAÇÃO DE EMPRESA AQUISIÇÃO DE ÁGUA MINERAL NATURAL
        PARA ATENDER AS NECESSIDADES DA SUPERINTENDÊNCIA MUNICIPAL DE TRÂNSITO.
        CONTRATADA: 74.096.231/0001-80 - WAMBERTO LOPES DE ARAUJO - ME
        VALOR: R$ 62.960,00
        DATA FINAL DE CONTRATO: 01/06/2018
        """

        headlines = response.css('tbody tr:not([class^="informacao"])')
        contract_details = response.css('tr.informacao')
        base_url = 'http://www.transparencia.feiradesantana.ba.gov.br'

        for headline, raw_details in zip(headlines, contract_details):
            contract_and_date = headline.css('th ::text').extract()
            contract = contract_and_date[0]
            starts_at = contract_and_date[1]
            details = self.clean_details(raw_details)
            document_url = raw_details.css('a.btn::attr(href)').get(default='')
            if document_url != '':
                document_url = f'{base_url}{document_url}'

            yield {
                'contract': contract,
                'starts_at': starts_at,
                'summary': details[0],
                'contractor': details[1],  # cnpj and company's name
                'value': details[2],
                'ends_at': details[3],
                'document_url': document_url
            }

    def clean_details(self, raw_details):
        labels = [
            'Objeto:',
            'Contratada:',
            'Valor:',
            'Data Final de Contrato:',
            'VISUALIZAR'
        ]

        valid_details = []
        for details in raw_details.css('p ::text').extract():
            details = details.strip()
            if details != '' and details not in labels:
                # assuming that all fields will be there
                valid_details.append(details)
        return valid_details
