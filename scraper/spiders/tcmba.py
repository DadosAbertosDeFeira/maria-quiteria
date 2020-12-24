from datetime import date, datetime

import scrapy
from lxml import etree
from lxml.etree import XMLParser
from parsel import Selector
from scraper.items import TcmBaDocumentsItem

from . import BaseSpider


def get_html_selector_from_xml(body, base_url):
    parser = XMLParser(strip_cdata=False)
    root = etree.fromstring(body, parser=parser, base_url=base_url)
    selector = Selector(root=root)
    html = selector.xpath("//update/text()").get()

    return Selector(text=html)


class DocumentsSpider(BaseSpider):
    name = "tcmba_documents"
    start_urls = ["https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam"]
    initial_date = date(2016, 1, 1)
    view_state = None
    city = "FEIRA DE SANTANA              "
    headers = {
        "Accept": "application/xml, text/xml, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
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
    custom_settings = {
        "ITEM_PIPELINES": {"scraper.pipelines.SessionAwareFilesPipeline": 1},
        "FILES_STORE": "files/",
    }
    download_delay = 0.25

    def parse(self, response):
        """Simula request da seleção do municipio."""
        cookies = [
            cookie.decode("utf-8").split(";")[0]
            for cookie in response.headers.getlist("Set-Cookie")
        ]
        jsessionid = cookies[0].split("=")[1]

        self.view_state = response.css("input#javax\.faces\.ViewState::attr(value)")[
            0
        ].get()

        custom_url = f"https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam;jsessionid={jsessionid}"

        self.headers["Cookie"] = "; ".join(cookies)

        body = {
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": "consultaPublicaTabPanel:consultaPublicaPCSearchForm:municipio",
            "javax.faces.partial.execute": "consultaPublicaTabPanel:consultaPublicaPCSearchForm:municipio",
            "javax.faces.partial.render": "consultaPublicaTabPanel:consultaPublicaPCSearchForm:unidadeJurisdicionada",
            "javax.faces.behavior.event": "itemSelect",
            "javax.faces.partial.event": "itemSelect",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm": "consultaPublicaTabPanel:consultaPublicaPCSearchForm",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:j_idt35-value": "true",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:PeriodicidadePC_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:PeriodicidadePC_input": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:competenciaPC_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:competenciaPC_input": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:tipoPC_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:tipoPC_input": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:municipio_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:municipio_input": self.city,
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:unidadeJurisdicionada_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:unidadeJurisdicionada_input": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:status_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:status_input": "",
            "javax.faces.ViewState": self.view_state,
        }

        yield scrapy.FormRequest(
            custom_url,
            formdata=body,
            callback=self.parse_params,
            dont_filter=True,
            headers=self.headers,
        )

    def parse_params(self, response):
        """Submete a pesquisa para acessar a lista de unidades jurisdicionadas."""
        body = {
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm": "consultaPublicaTabPanel:consultaPublicaPCSearchForm",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:j_idt35-value": "true",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:PeriodicidadePC_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:PeriodicidadePC_input": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:competenciaPC_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:competenciaPC_input": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:tipoPC_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:tipoPC_input": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:municipio_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:municipio_input": self.city,
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:unidadeJurisdicionada_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:unidadeJurisdicionada_input": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:status_focus": "",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:status_input": "",
            "javax.faces.ViewState": self.view_state,
            "javax.faces.source": "consultaPublicaTabPanel:consultaPublicaPCSearchForm:searchButton",
            "javax.faces.partial.event": "click",
            "javax.faces.partial.execute": "consultaPublicaTabPanel:consultaPublicaPCSearchForm:searchButton @component",
            "javax.faces.partial.render": "@component",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:j_idt76": "1",
            "org.richfaces.ajax.component": "consultaPublicaTabPanel:consultaPublicaPCSearchForm:searchButton",
            "consultaPublicaTabPanel:consultaPublicaPCSearchForm:searchButton": "consultaPublicaTabPanel:consultaPublicaPCSearchForm:searchButton",
            "rfExt": "null",
            "AJAX:EVENTS_COUNT": "1",
            "javax.faces.partial.ajax": "true",
        }

        # TODO pegar "Foram encontrados 71228 resultados" para conferir com raspados
        # consultaPublicaTabPanel\:consultaPublicaDataTablePanel_body > div:nth-child(2)

        # TODO páginas
        # máximo de páginas: span.rf-insl-mx

        # TODO checar se já chegou no máximo de páginas

        # TODO request da paginação
        # {
        #     "consultaPublicaTabPanel:j_idt215": "consultaPublicaTabPanel:j_idt215",
        #     "consultaPublicaTabPanel:j_idt215:j_idt216": "5",  # FIXME número da página
        #     "javax.faces.ViewState": self.view_state,
        #     "javax.faces.source": "consultaPublicaTabPanel:j_idt215:j_idt216",
        #     "javax.faces.partial.event": "change",
        #     "javax.faces.partial.execute": "consultaPublicaTabPanel:j_idt215:j_idt216 @component",
        #     "javax.faces.partial.render": "@component",
        #     "javax.faces.behavior.event": "change",
        #     "org.richfaces.ajax.component": "consultaPublicaTabPanel:j_idt215:j_idt216",
        #     "rfExt": "null",
        #     "AJAX:EVENTS_COUNT": "1",
        #     "javax.faces.partial.ajax": "true"
        # }

        # para cada página...
        yield scrapy.FormRequest(
            "https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam",
            formdata=body,
            callback=self.parse_units,
            dont_filter=True,
            headers=self.headers,
        )

    def parse_units(self, response):
        """Acessa as unidades jurisdicionadas."""
        res = get_html_selector_from_xml(response.body, response.url)
        select_unit_buttons = res.xpath(
            "//a[contains(@id, 'consultaPublicaTabPanel:consultaPublicaDataTable')]"
        )

        # TODO fazer a coleta dinamicamente
        # for button in select_unit_buttons:
        #     button_id = button.css("::attr(id)").get()

        button_id = "consultaPublicaTabPanel:consultaPublicaDataTable:0:j_idt81:selecionarPrestacao"  # FIXME
        form_id = "consultaPublicaTabPanel:consultaPublicaDataTable:0:j_idt81"  # FIXME

        body = {
            form_id: form_id,
            "javax.faces.ViewState": self.view_state,
            "javax.faces.source": button_id,
            "javax.faces.partial.event": "click",
            "javax.faces.partial.execute": f"{form_id}:selecionarPrestacao @component",
            "javax.faces.partial.render": "@component",
            "org.richfaces.ajax.component": button_id,
            button_id: button_id,
            "rfExt": "null",
            "AJAX:EVENTS_COUNT": "1",
            "javax.faces.partial.ajax": "true",
        }

        yield scrapy.FormRequest(
            "https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam",
            formdata=body,
            callback=self.parse_documents,
            dont_filter=True,
            headers=self.headers,
        )

    def parse_documents(self, response):
        """Acessa a lista de documentos de uma unidade jurisdicionada."""
        res = get_html_selector_from_xml(response.body, response.url)
        rows = res.css("tr.ui-widget-content")

        unit = res.css(
            "#consultaPublicaTabPanel\:unidadeJurisdicionadaDecoration\:unidadeJurisdicionada::text"
        ).get()

        for row in rows:
            form_id = row.css("form::attr(id)").get()

            if form_id:
                labels = row.css("td[role='gridcell']::text").getall()
                # esperamos algo como:
                # ['\n', 'Documentos', '01 - DEMONSTRATIVO.pdf', 'MICHELE REIS', '23/12/2020']

                document_info = {
                    "category": labels[1],
                    "filename": labels[2],
                    "inserted_by": labels[3],
                    "inserted_at": labels[4],
                    "unit": unit,
                }
                body = {
                    form_id: form_id,
                    "javax.faces.ViewState": self.view_state,
                    "javax.faces.source": f"{form_id}:downloadDocBinario",
                    "javax.faces.partial.event": "click",
                    "javax.faces.partial.execute": f"{form_id}:downloadDocBinario @component",
                    "javax.faces.partial.render": "@component",
                    "org.richfaces.ajax.component": f"{form_id}:downloadDocBinario",
                    f"{form_id}:downloadDocBinario": f"{form_id}:downloadDocBinario",
                    "rfExt": "null",
                    "AJAX:EVENTS_COUNT": "1",
                    "javax.faces.partial.ajax": "true",
                }

                yield scrapy.FormRequest(
                    "https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam",
                    formdata=body,
                    callback=self.parse_document_download,
                    dont_filter=True,
                    headers=self.headers,
                    meta={"document_info": document_info},
                )

    def parse_document_download(self, response):
        """Faz o download de um documento."""
        cookies = [
            cookie.decode("utf-8").split(";")[0]
            for cookie in response.headers.getlist("Set-Cookie")
        ]
        current_cookies = "; ".join(cookies)
        previous_cookies = response.request.headers["Cookie"].decode("utf-8")

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Cookie": f"{previous_cookies}; {current_cookies}",
            "DNT": "1",
            "Host": "e.tcm.ba.gov.br",
            "Referer": "https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        }

        yield TcmBaDocumentsItem(
            crawled_at=datetime.now(),
            crawled_from=response.url,
            file_request={
                "url": "https://e.tcm.ba.gov.br/epp/PdfReadOnly/downloadDocumento.seam",
                "headers": headers,
                "filename": response.meta["document_info"]["filename"],
            },
            category=response.meta["document_info"]["category"],
            filename=response.meta["document_info"]["filename"],
            inserted_by=response.meta["document_info"]["inserted_by"],
            inserted_at=response.meta["document_info"]["inserted_at"],
            unit=response.meta["document_info"]["unit"],
        )
