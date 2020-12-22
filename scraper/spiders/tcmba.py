from datetime import date
from pprint import pprint
import scrapy

from lxml.etree import XMLParser
from lxml import etree
from parsel import Selector

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
    cookies = None
    city = "FEIRA DE SANTANA              "

    def parse(self, response):
        """Simula request da seleção do municipio."""
        self.cookies = [
            cookie.decode("utf-8").split(";")[0]
            for cookie in response.headers.getlist("Set-Cookie")
        ]
        jsessionid = self.cookies[0].split("=")[1]

        self.view_state = response.css("input#javax\.faces\.ViewState::attr(value)")[
            0
        ].get()

        custom_url = f"https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam;jsessionid={jsessionid}"

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
            "Cookie": "; ".join(self.cookies)
        }

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
            "javax.faces.ViewState": self.view_state
        }

        print("------------------------------- ")
        # pprint(response.body)
        print(self.view_state)

        yield scrapy.FormRequest(
            custom_url, formdata=body, callback=self.parse_params, dont_filter=True,
            headers=headers,
            cookies=self.cookies,
        )

    def parse_params(self, response):
        """Submete a pesquisa para acessar a lista de unidades jurisdicionadas."""
        headers = {
            "Accept": "*/*",
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
            "Cookie": "; ".join(self.cookies)
        }

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
            "javax.faces.partial.ajax": "true"
        }

        print("------------------------------- ")

        yield scrapy.FormRequest(
            "https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam",
            formdata=body, callback=self.parse_units, dont_filter=True,
            headers=headers,
            cookies=self.cookies,
        )

    def parse_units(self, response):
        print("------------------------------- ")

        # res.css("td.rf-dt-c ::text").getall()
        res = get_html_selector_from_xml(response.body, response.url)

        select_unit_buttons = res.xpath("//a[contains(@id, 'consultaPublicaTabPanel:consultaPublicaDataTable')]")

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
            "javax.faces.partial.ajax": "true"
        }
        print("------------------------------- ")

        pprint(response.body)

        headers = {
            "Accept": "*/*",
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
            "Cookie": "; ".join(self.cookies)
        }

        yield scrapy.FormRequest(
            "https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam",
            formdata=body, callback=self.parse_documents, dont_filter=True,
            headers=headers,
            cookies=self.cookies,
        )

    def parse_documents(self, response):
        res = get_html_selector_from_xml(response.body, response.url)
        rows = res.css("tr.ui-widget-content")
        form_ids = res.xpath("//form[contains(@id, 'consultaPublicaTabPanel:tabelaDocumentos')]")

        # for row in rows:
        #     form_id = row.xpath("//form[contains(@id, 'consultaPublicaTabPanel:tabelaDocumentos')]")
        #     labels = row.css("td::text").getall()

        form_id = "consultaPublicaTabPanel:tabelaDocumentos:0:j_idt272"

        print(response.body)

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
            "javax.faces.partial.ajax": "true"
        }

        headers = {
            "Accept": "*/*",
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
            "Cookie": "; ".join(self.cookies)
        }

        yield scrapy.FormRequest(
            "https://e.tcm.ba.gov.br/epp/ConsultaPublica/listView.seam",
            formdata=body, callback=self.parse_document_download, dont_filter=True,
            headers=headers,
            cookies=self.cookies,
        )

    def parse_document_download(self, response):
        res = get_html_selector_from_xml(response.body, response.url)

        # mandar o <a> para /epp/PdfReadOnly/downloadDocumento.seam?
        # TODO /epp/PdfReadOnly/downloadDocumento.seam
        # <partial-response><changes><update id="consultaPublicaTabPanel:tabelaDocumentos:9:j_idt272:downloadDocBinario">
        # <![CDATA[<a href="#" id="consultaPublicaTabPanel:tabelaDocumentos:9:j_idt272:downloadDocBinario" name="consultaPublicaTabPanel:tabelaDocumentos:9:j_idt272:downloadDocBinario" onclick="jsf.util.chain(this,event,&quot;infox.showLoading();&quot;,&quot;RichFaces.ajax(\&quot;consultaPublicaTabPanel:tabelaDocumentos:9:j_idt272:downloadDocBinario\&quot;,event,{\&quot;incId\&quot;:\&quot;1\&quot;,\&quot;status\&quot;:\&quot;:status\&quot;} )&quot;);return false;" class="opacityHover" style="margin-right: 0.3em;"><img src="/epp/resources/styleSkinInfox/azul/imagens/view.png" alt="" title="Desembolso Extra.pdf (7,89 Kb)" /></a>]]></update><update id="javax.faces.ViewState"><![CDATA[2375279134312630331:4844868770498808673]]></update><extension id="org.richfaces.extension"><complete>infox.hideLoading(); window.open('/epp/PdfReadOnly/downloadDocumento.seam');;</complete><render>consultaPublicaTabPanel:tabelaDocumentos:9:j_idt272:downloadDocBinario</render></extension></changes></partial-response>
