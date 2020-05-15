from datetime import date, datetime

from scraper.items import GazetteItem, LegacyGazetteItem
from scrapy import Request

from datasets.parsers import from_str_to_date

from . import BaseSpider
from .utils import replace_query_param


class LegacyGazetteSpider(BaseSpider):
    """Coleta diário oficial de Feira de Santana até 2015.

    Years: 1999 to 2015
    Example: http://www.feiradesantana.ba.gov.br/seadm/leis.asp?acao=ir&p=24&ano=2015
    """

    name = "legacy_gazettes"
    start_urls = [
        f"http://www.feiradesantana.ba.gov.br/servicos.asp?"
        f"acao=ir&s=a&link=seadm/leis.asp&p=1&"
        f"txtlei=%27Pesquisar%20pelo%20n%FAmero%20do%20ato%20ou%20palavra-chave%27"
        f"&cat=0"
        f"&ano={year}#links"
        for year in range(1999, 2016)
    ]

    def parse(self, response):
        if "SEM INFORMA" not in response.text:  # it means page found
            events, urls = self.extract_events(response)
            for event, url in zip(events, urls):
                yield LegacyGazetteItem(
                    title=event["event"],
                    published_on=event["published_on"],
                    date=from_str_to_date(event["date"]),
                    details=url["details"],
                    file_urls=[url["url"]],
                    crawled_at=datetime.now(),
                    crawled_from=response.url,
                )

            current_page = self.get_current_page(response)
            last_page = response.xpath("//table/tr[10]/td/ul/li/a/text()")

            if current_page and last_page:
                last_page = int(last_page[-1].get().strip())
                next_page = int(current_page.strip()) + 1

                if next_page <= last_page:
                    url = replace_query_param(response.url, "p", next_page)
                    yield response.follow(url, callback=self.parse)

    def get_current_page(self, response):
        current_page = response.xpath(
            "//table/tr[10]/td/ul/li[contains(@class, 'current')]/a/text()"
        ).get()
        if current_page is None:
            current_page = response.css("li.current ::text").get()
        if current_page is None:
            current_page = response.css("ul.pagination li.active ::text").get()
        return current_page

    def extract_events(self, response):
        events = []
        infos = response.xpath(
            "//form/table/tr[8]/td/table/tr/td/table/tr/td/table/tr/td/span"
        )
        for info in infos:
            text = info.css(" ::text").extract()
            event = text[0].strip()
            published_on = None
            date = None
            if len(text) > 3:
                published_on = text[3].replace("-", "").strip()
                date = text[-1].strip()
            events.append({"event": event, "published_on": published_on, "date": date})

        events_urls = []
        urls = response.xpath(
            "//form/table/tr[8]/td/table/tr/td/table/tr/td/table/tr/td[1]/a"
        )
        for label_and_url in urls:
            details = label_and_url.css(" ::text").extract()
            details = " ".join(details).strip()
            url = label_and_url.css(" ::attr(href)").extract_first()
            events_urls.append({"details": details, "url": url})
        return events, events_urls


class ExecutiveAndLegislativeGazetteSpider(BaseSpider):
    """Coleta o Diário Oficial dos poderes executivo e legislativo."""

    name = "gazettes"
    allowed_domains = ["diariooficial.feiradesantana.ba.gov.br"]
    start_urls = ["http://www.diariooficial.feiradesantana.ba.gov.br"]
    powers = {"executivo": 1, "legislativo": 2}
    last_page = 1
    handle_httpstatus_list = [302]
    initial_date = date(2015, 1, 1)

    def parse(self, response):
        self.logger.info(f"Data inicial: {self.start_date}")

        gazette_table = response.css(".style166")
        gazettes_links = gazette_table.xpath("a//@href").extract()
        dates = gazette_table.css("a::text").extract()

        limit_date_by_power = {}
        for url, gazette_date in zip(gazettes_links, dates):
            date_obj = datetime.strptime(gazette_date, "%d/%m/%Y")
            if date_obj.date() >= self.start_date:
                edition = self.extract_edition(url)
                power = self.extract_power(url)
                power_id = self.powers[power]

                if date_obj.date() == self.start_date:
                    limit_date_by_power[power] = date_obj.date()

                gazette = dict(
                    date=gazette_date,
                    power=power,
                    url=response.urljoin(url),
                    file_url=response.urljoin(f"abrir.asp?edi={edition}&p={power_id}"),
                )

                yield Request(
                    gazette["url"],
                    callback=self.parse_details,
                    meta={"gazette": gazette},
                )

        # as datas do legislativo e do executivo podem não estar na mesma página
        if len(limit_date_by_power) < 2:
            current_page_selector = "#pages ul li.current::text"
            current_page = response.css(current_page_selector).extract_first()
            if current_page:
                next_page = int(current_page) + 1
                next_page_url = response.urljoin(f"/?p={next_page}")

                if next_page > self.last_page:
                    self.last_page = next_page
                    yield Request(next_page_url)

    def parse_details(self, response):
        gazette = response.meta["gazette"]

        gazette["year_and_edition"] = (
            response.css("span.style4 ::text").extract()[1].strip()
        )
        titles = response.xpath("//tr/td/table/tr/td[@colspan='2']/text()").extract()
        descriptions = response.css("td.destaqt ::text").extract()

        events = []
        while titles:
            events.append(
                {
                    "title": titles.pop(0).strip(),
                    "secretariat": descriptions.pop(0).strip(),
                    "summary": descriptions.pop(0).strip(),
                }
            )
            titles.pop(0)

        if gazette.get("events") is None:
            gazette["events"] = events
        else:
            gazette["events"].extend(events.copy())

        current_page = response.css("ul li.current ::text").extract_first()
        last_page = response.css("ul li:last-child ::text").extract_first()
        if current_page:
            current_page = current_page.strip()
            last_page = last_page.strip()
            if current_page != last_page:
                next_page = int(current_page) + 1
                url = response.css("ul li a::attr(href)").extract_first()
                url = replace_query_param(url, "p", next_page)

                yield Request(
                    response.urljoin(url),
                    callback=self.parse_details,
                    meta={"gazette": gazette},
                )
            else:
                gazette_item = GazetteItem(
                    date=from_str_to_date(gazette["date"]),
                    power=gazette["power"],
                    year_and_edition=gazette["year_and_edition"],
                    events=gazette["events"],
                    crawled_at=datetime.now(),
                    crawled_from=response.url,
                )
                yield Request(
                    gazette["file_url"],
                    callback=self.parse_document_url,
                    meta={"gazette": gazette_item},
                )

    def parse_document_url(self, response):
        gazette = response.meta["gazette"]
        url = response.headers["Location"].decode("utf-8")
        gazette["file_urls"] = [url.replace("https", "http")]
        return gazette

    def extract_power(self, url):
        if url.find("st=1") != -1:
            return "executivo"
        return "legislativo"

    def extract_edition(self, url):
        edition_index = url.find("edicao=") + len("edicao=")
        edition = url[edition_index:]
        return edition
