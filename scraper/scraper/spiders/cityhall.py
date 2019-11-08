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
