from datetime import date, datetime, timedelta

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import F

CITY_COUNCIL_EVENT_TYPE = (
    ("sessao_ordinaria", "Sessão Ordinária"),
    ("ordem_do_dia", "Ordem do Dia"),
    ("sessao_solene", "Sessão Solene"),
    ("sessao_especial", "Sessão Especial"),
    ("audiencia_publica", "Audiência Pública"),
)

BID_MODALITIES = (
    ("tomada_de_precos", "Tomada de Preço"),
    ("pregao_presencial", "Pregão Presencial"),
    ("pregao_eletronico", "Pregão Eletrônico"),
    ("leilao", "Leilão"),
    ("inexigibilidade", "Inexigibilidade"),
    ("dispensada", "Dispensada"),
    ("convite", "Convite"),
    ("concurso", "Concurso"),
    ("concorrencia", "Concorrência"),
    ("chamada_publica", "Chamada Pública"),
)

EXPENSE_MODALITIES = (
    ("convenio", "Convênio"),
    ("tomada_de_precos", "Tomada de Preço"),
    ("pregao", "Pregão"),
    ("inexigibilidade", "Inexigibilidade"),
    ("convite", "Convite"),
    ("concorrencia", "Concorrência"),
    ("dispensa", "Dispensa"),
    ("isento", "Isento"),
)


class File(models.Model):
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    url = models.URLField("Arquivo")
    content = models.TextField("Conteúdo", null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    checksum = models.CharField(max_length=128, null=True, blank=True)
    s3_url = models.URLField("URL externa", null=True, blank=True)
    s3_file_path = models.CharField(max_length=300, null=True, blank=True)

    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        verbose_name = "Arquivo"
        verbose_name_plural = "Arquivos"
        indexes = [GinIndex(fields=["search_vector"])]
        unique_together = ("url", "content_type", "object_id")

    def __repr__(self):
        return f"[{self.content_type}] {self.url}"

    def __str__(self):
        return f"Arquivo ({self.pk}) de {self.content_type} ({self.object_id})"


class DatasetMixin(models.Model):
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    crawled_at = models.DateTimeField("Coletado em")
    crawled_from = models.URLField("Fonte")
    notes = models.TextField("Anotações", null=True, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def last_collected_item_date(cls):
        try:
            field = cls._meta.get_latest_by
            kwargs = {
                f"{field}__isnull": False,
            }
            found = cls.objects.filter(**kwargs).latest()
            if found:
                value = getattr(found, field)
                if isinstance(value, datetime):
                    return value.date()
                return value
        except cls.DoesNotExist:
            return
        except TypeError:
            raise NotImplementedError(
                "Especifique um `get_latest_by` no Meta deste model"
            )


class CityCouncilAgenda(DatasetMixin):
    date = models.DateField("Data")
    details = models.TextField("Detalhes", null=True, blank=True)
    event_type = models.CharField(
        "Tipo do evento",
        max_length=20,
        choices=CITY_COUNCIL_EVENT_TYPE,
        null=True,
        blank=True,
    )
    title = models.CharField("Título", max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Câmara de Vereadores - Agenda"
        verbose_name_plural = "Câmara de Vereadores - Agendas"
        get_latest_by = "date"

    def __repr__(self):
        return f"{self.date} {self.event_type} {self.title}"

    @classmethod
    def last_collected_item_date(cls):
        """Retorna primeiro dia do ano do mais recente item coletado."""
        try:
            latest = cls.objects.latest()
            if latest.date:
                return date(latest.date.year, 1, 1)
        except cls.DoesNotExist:
            return


class CityCouncilAttendanceList(DatasetMixin):
    STATUS = (
        ("presente", "Presente"),
        ("falta_justificada", "Falta Justificada"),
        ("licenca_justificada", "Licença Justificada"),
        ("ausente", "Ausente"),
    )
    date = models.DateField("Data")
    description = models.CharField("Descrição", max_length=200, null=True, blank=True)
    council_member = models.CharField("Vereador", max_length=200)
    status = models.CharField("Situação", max_length=20, choices=STATUS)

    class Meta:
        verbose_name = "Câmara de Vereadores - Lista de Presença"
        verbose_name_plural = "Câmara de Vereadores - Listas de Presença"
        get_latest_by = "date"

    def __repr__(self):
        return f"{self.date} {self.council_member} {self.status}"

    @classmethod
    def last_collected_item_date(cls):
        """Retorna primeiro dia do ano do mais recente item coletado."""
        try:
            latest = cls.objects.latest()
            if latest.date:
                return date(latest.date.year, 1, 1)
        except cls.DoesNotExist:
            return


class CityCouncilContract(DatasetMixin):
    external_code = models.PositiveIntegerField("Código externo")
    description = models.TextField("Descrição", null=True, blank=True)
    details = models.TextField("Objeto do contrato", null=True, blank=True)
    company_or_person_document = models.CharField(
        "CNPJ ou CPF", max_length=50, null=True, blank=True
    )
    company_or_person = models.TextField("Empresa ou pessoa", null=True, blank=True)
    value = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    start_date = models.DateField("Data de início")
    end_date = models.DateField("Data final")
    excluded = models.BooleanField("Excluído?", default=False)

    class Meta:
        verbose_name = "Câmara de Vereadores - Contrato"
        verbose_name_plural = "Câmara de Vereadores - Contratos"
        get_latest_by = "start_date"

    def __repr__(self):
        interval = f"{self.start_date} {self.end_date}"
        return f"{interval} {self.description} {self.company_or_person}"

    def __str__(self):
        interval = f"{self.start_date} {self.end_date}"
        return f"{interval} {self.description} {self.company_or_person}"


class CityCouncilExpense(DatasetMixin):
    PHASE = (
        ("empenho", "Empenho"),
        ("liquidacao", "Liquidação"),
        ("pagamento", "Pagamento"),
    )
    published_at = models.DateField("Publicado em", null=True, blank=True)
    phase = models.CharField("Fase", max_length=20, choices=PHASE)
    phase_code = models.CharField(
        "Código da fase", max_length=20, null=True, blank=True
    )
    company_or_person = models.TextField("Empresa ou pessoa", null=True, blank=True)
    value = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    number = models.CharField("Número", max_length=50, null=True, blank=True)
    document = models.CharField("CNPJ ou CPF", max_length=50, null=True, blank=True)
    date = models.DateField("Data")
    process_number = models.CharField(
        "Número do processo", max_length=50, null=True, blank=True
    )
    summary = models.TextField("Descrição", null=True, blank=True)
    legal_status = models.CharField("Natureza", max_length=200, null=True, blank=True)
    function = models.CharField("Função", max_length=50, null=True, blank=True)
    subfunction = models.CharField("Subfunção", max_length=50, null=True, blank=True)
    resource = models.CharField("Fonte", max_length=200, null=True, blank=True)
    subgroup = models.CharField("Subgrupos", max_length=100, null=True, blank=True)
    group = models.CharField("Grupo", max_length=100, null=True, blank=True)
    budget_unit = models.PositiveIntegerField("Unidade orçamentária", default=101)
    modality = models.CharField(
        "Modalidade", max_length=50, null=True, blank=True, choices=EXPENSE_MODALITIES
    )
    excluded = models.BooleanField("Excluído?", default=False)
    external_file_code = models.CharField(
        "Código do arquivo (externo)", max_length=50, null=True, blank=True
    )
    external_file_line = models.CharField(
        "Linha do arquivo (externo)", max_length=50, null=True, blank=True
    )

    class Meta:
        verbose_name = "Câmara de Vereadores - Despesa"
        verbose_name_plural = "Câmara de Vereadores - Despesas"
        get_latest_by = "date"

    def __repr__(self):
        return f"{self.date} {self.phase} {self.company_or_person} {self.value}"

    def __str__(self):
        return f"{self.date} {self.phase} {self.company_or_person} {self.value}"


class CityCouncilMinute(DatasetMixin):
    date = models.DateField("Data")
    title = models.CharField("Título", max_length=300, null=True, blank=True)
    event_type = models.CharField(
        "Tipo de evento",
        max_length=20,
        choices=CITY_COUNCIL_EVENT_TYPE,
        null=True,
        blank=True,
    )
    files = GenericRelation(File)
    file_url = models.URLField("Endereço (URL)", null=True, blank=True)
    file_content = models.TextField("Conteúdo do arquivo", null=True, blank=True)

    class Meta:
        verbose_name = "Câmara de Vereadores - Atas"
        verbose_name_plural = "Câmara de Vereadores - Atas"
        get_latest_by = "date"

    def __repr__(self):
        return f"{self.date} {self.title}"

    def __str__(self):
        return f"{self.date} {self.title}"


class Gazette(DatasetMixin):
    POWER_TYPE = (
        ("executivo", "Poder Executivo"),
        ("legislativo", "Poder Legislativo"),
    )
    date = models.DateField("Data", null=True)
    power = models.CharField("Poder", max_length=25, choices=POWER_TYPE)
    year_and_edition = models.CharField("Ano e edição", max_length=100)
    is_legacy = models.BooleanField("É do site antigo?", default=False)
    file_url = models.URLField("Endereço (URL)", null=True, blank=True)
    file_content = models.TextField("Conteúdo do arquivo", null=True, blank=True)
    files = GenericRelation(File)
    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        verbose_name = "Diário Oficial"
        verbose_name_plural = "Diários Oficiais"
        get_latest_by = "date"
        ordering = [F("date").desc(nulls_last=True)]

        indexes = [GinIndex(fields=["search_vector"])]

    def __repr__(self):
        return f"{self.date} {self.power} {self.year_and_edition}"

    def __str__(self):
        return f"{self.date} {self.power} {self.year_and_edition}"


class GazetteEvent(DatasetMixin):
    gazette = models.ForeignKey(Gazette, on_delete=models.CASCADE)
    title = models.CharField("Título", max_length=300, null=True, blank=True)
    secretariat = models.CharField("Secretaria", max_length=100, null=True, blank=True)
    summary = models.TextField("Sumário", null=True, blank=True)
    published_on = models.CharField(
        "Publicado em", max_length=100, null=True, blank=True
    )

    class Meta:
        verbose_name = "Diário Oficial - Evento"
        verbose_name_plural = "Diário Oficial - Eventos"

    def __repr__(self):
        gazette_info = f"{self.gazette.power} {self.gazette.year_and_edition}"
        return f"[{gazette_info}] {self.title} {self.secretariat}"


class CityHallBid(DatasetMixin):
    session_at = models.DateTimeField("Sessão Data / Horário", null=True)
    public_agency = models.CharField("Órgão", max_length=200)
    description = models.TextField("Descrição", null=True, blank=True)
    modality = models.CharField(
        "Modalidade", max_length=60, choices=BID_MODALITIES, null=True, blank=True
    )
    codes = models.CharField("Códigos", max_length=300)
    file_url = models.URLField("Arquivo", null=True, blank=True)
    file_content = models.TextField("Conteúdo", null=True, blank=True)
    files = GenericRelation(File)

    class Meta:
        verbose_name = "Prefeitura - Licitação"
        verbose_name_plural = "Prefeitura - Licitações"
        get_latest_by = "session_at"

    def __repr__(self):
        return f"{self.session_at} {self.modality} {self.public_agency}"

    def __str__(self):
        return f"{self.session_at} {self.modality} {self.public_agency}"

    @classmethod
    def last_collected_item_date(cls):
        """Retorna data para início da coleta.

        Dado que as licitações são constantemente atualizadas e nós não temos
        um maneira mais simples de verificar os últimos itens atualizados,
        vamos assumir que os últimos seis meses é um período razoável para
        ter licitações sendo atualizadas.
        """
        try:
            # checa se existe algum registro antes
            cls.objects.latest()
            return date.today() - timedelta(days=180)
        except cls.DoesNotExist:
            return


class CityHallBidEvent(DatasetMixin):
    bid = models.ForeignKey(
        CityHallBid, on_delete=models.CASCADE, related_name="events",
    )
    published_at = models.DateTimeField("Publicado em", null=True)
    summary = models.TextField("Descrição", null=True, blank=True)
    files = GenericRelation(File)
    file_url = models.URLField("Arquivo", null=True, blank=True)
    file_content = models.TextField("Conteúdo", null=True, blank=True)

    class Meta:
        verbose_name = "Prefeitura - Licitação - Histórico"
        verbose_name_plural = "Prefeitura - Licitações - Históricos"

    def __repr__(self):
        bid_info = f"{self.bid.session_at} {self.bid.modality}"
        return f"[{bid_info}] {self.published_at} {self.summary}"

    @property
    def file_urls(self):
        return [file_.url for file_ in self.files.all()]


class CityCouncilBid(DatasetMixin):
    external_code = models.CharField("Código externo", max_length=10)
    modality = models.CharField(
        "Modalidade", max_length=60, choices=BID_MODALITIES, null=True, blank=True
    )
    code = models.CharField("Código da licitação", max_length=15)
    code_type = models.CharField("Código do tipo da licitação", max_length=15)
    description = models.TextField("Descrição (objeto)")
    session_at = models.DateTimeField("Sessão Data / Horário", null=True)
    excluded = models.BooleanField("Excluído?", default=False)

    class Meta:
        verbose_name = "Câmara de Vereadores - Licitação"
        verbose_name_plural = "Câmara de Vereadores - Licitações"
        get_latest_by = "session_at"

    def __repr__(self):
        model_name = self._meta.verbose_name
        return f"{model_name} {self.session_at} {self.code} {self.code_type}"

    def __str__(self):
        model_name = self._meta.verbose_name
        return f"{model_name} {self.session_at} {self.code} {self.code_type}"
