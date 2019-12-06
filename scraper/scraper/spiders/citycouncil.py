import scrapy


class AgendaSpider(scrapy.Spider):
    name = "agenda"
    start_urls = ["https://www.feiradesantana.ba.leg.br/agenda"]

    @staticmethod
    def get_type(event_title):
        if "ordem do dia" in event_title.lower():
            return "ordem_do_dia"
        if "sessão solene" in event_title.lower():
            return "sessao_solene"
        if "audiência pública" in event_title.lower():
            return "audiencia_publica"
        return "not_found"

    def parse(self, response):
        extracted_years = response.css("select#ano option ::text").extract()
        years = []
        for year in extracted_years:
            try:
                years.append(int(year))
            except ValueError:
                pass

        for year in range(min(years), max(years) + 1):
            for month in range(1, 13):
                url = f"https://www.feiradesantana.ba.leg.br/"
                "agenda?mes={month}&ano={year}&Acessar=OK"
                yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        event_details = response.css("div.feature-box")
        dates = response.xpath("//table/tbody/tr/td[1]/strong/text()").getall()
        event_titles = response.xpath("//table/tbody/tr/td[2]/p/strong/text()").getall()

        for details, date, title in zip(event_details, dates, event_titles):
            events = [
                line.strip()
                for line in details.css("p ::text").getall()
                if line.strip() != ""
            ]

            yield {
                "url": response.url,
                "date": date,
                "details": " ".join(events),
                "title": title.strip(),
                "type": self.get_type(title),
            }
