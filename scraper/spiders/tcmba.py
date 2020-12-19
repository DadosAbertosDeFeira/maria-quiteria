from datetime import date

import scrapy

from . import BaseSpider


class DocumentsSpider(BaseSpider):
    name = "tcmba_documents"
    start_urls = ["https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam"]
    initial_date = date(2016, 1, 1)
    view_state = None

    def parse(self, response):
        cookies = [
            cookie.decode("utf-8").split(";")[0]
            for cookie in response.headers.getlist("Set-Cookie")
        ]
        jsessionid = cookies[0].split("=")[1]

        self.view_state = response.css("input#javax\.faces\.ViewState::attr(value)")[
            0
        ].get()

        url = f"https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam;jsessionid={jsessionid}"

        headers = {
            "Accept": "*/*",
            "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "DNT": "1",
            "Faces-Request": "partial/ajax",
            "Origin": "https://e.tcm.ba.gov.br",
            "Referer": "https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
            "X-Requested-With": "XMLHttpRequest",
        }
        body = (
            f"j_idt15=j_idt15&javax.faces.ViewState={self.view_state.replace(':', '%3A')}"
            f"&javax.faces.source=j_idt15%3Aj_idt16&javax.faces.partial.execute=j_idt15%3Aj_idt16%20%40component"
            f"&javax.faces.partial.render=%40component&org.richfaces.ajax.component=j_idt15%3Aj_idt16"
            f"&j_idt15%3Aj_idt16=j_idt15%3Aj_idt16&rfExt=null&AJAX%3AEVENTS_COUNT=1&javax.faces.partial.ajax=true"
        )
        yield scrapy.Request(
            url,
            method="POST",
            body=body,
            headers=headers,
            cookies=cookies,
            callback=self.parse_unit_results,
            dont_filter=True,
        )

    def parse_unit_results(self, response):
        print("Got it")
