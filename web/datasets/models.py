from datetime import date, datetime, timedelta

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import F
from simple_history.models import HistoricalRecords

CITY_COUNCIL_EVENT_TYPE = (
    ("sessao_ordinaria", "Sessão Ordinária"),
    ("ordem_do_dia", "Ordem do Dia"),
    ("sessao_solene", "Sessão Solene"),
    ("sessao_especial", "Sessão Especial"),
    ("audiencia_publica", "Audiência Pública"),
    ("sessao_extraordinaria", "Sessão Extraordinária"),
    ("termo_de_encerramento", "Termo de Encerramento"),
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

REVENUE_TYPES = (
    ("orcamentaria", "Orçamentária"),
    ("nao_orcamentaria", "Não-orçamentária"),
    ("transferencia", "Transferência"),
)

SYNC_SOURCE = (
    ("camara", "Câmara Municipal"),
    ("prefeitura", "Prefeitura"),
)


class File(models.Model):
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    url = models.URLField("URL do arquivo", db_index=True)
    content = models.TextField("Conteúdo", null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")
    checksum = models.CharField(max_length=128, null=True, blank=True)
    s3_url = models.URLField("URL externa", max_length=600, null=True, blank=True)
    s3_file_path = models.CharField(
        "Caminho interno", max_length=400, null=True, blank=True
    )
    external_code = models.CharField(
        "Código externo", max_length=10, null=True, blank=True, db_index=True
    )
    original_filename = models.CharField(
        "Nome do arquivo", max_length=200, null=True, blank=True, db_index=True
    )
    local_path = models.CharField(max_length=350, null=True, blank=True)

    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        verbose_name = "Arquivo"
        verbose_name_plural = "Arquivos"
        indexes = [GinIndex(fields=["search_vector"])]
        unique_together = ("url", "content_type", "object_id", "original_filename")
        ordering = ["-created_at"]

    def __repr__(self):
        return f"[{self.content_type}] {self.original_filename} {self.url}"

    def __str__(self):
        obj_label = f"{self.content_type} ({self.object_id})"
        return f"Arquivo {self.original_filename} ({self.pk}) de {obj_label}"


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
            kwargs = {f"{field}__isnull": False}
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
        max_length=30,
        choices=CITY_COUNCIL_EVENT_TYPE,
        null=True,
        blank=True,
        db_index=True,
    )
    title = models.CharField("Título", max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Câmara de Vereadores - Agenda"
        verbose_name_plural = "Câmara de Vereadores - Agendas"
        ordering = ["-date"]
        get_latest_by = "date"

    def __repr__(self):
        return f"{self.date} {self.event_type} {self.title}"

    def __str__(self):
        return f"Agenda para {self.title.capitalize()}"

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
    council_member = models.CharField("Vereador", max_length=200, db_index=True)
    status = models.CharField("Situação", max_length=20, choices=STATUS, db_index=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Câmara de Vereadores - Lista de Presença"
        verbose_name_plural = "Câmara de Vereadores - Listas de Presença"
        get_latest_by = "date"
        ordering = ["-date"]

    def __repr__(self):
        return f"{self.date} {self.council_member} {self.status}"

    def __str__(self):
        return f"Presença em {self.date} - {self.council_member}"

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
    external_code = models.PositiveIntegerField(
        "Código externo", unique=True, db_index=True
    )
    description = models.TextField("Descrição", null=True, blank=True, db_index=True)
    details = models.TextField(
        "Objeto do contrato", null=True, blank=True, db_index=True
    )
    company_or_person_document = models.CharField(
        "CNPJ ou CPF", max_length=50, null=True, blank=True, db_index=True
    )
    company_or_person = models.TextField(
        "Empresa ou pessoa", null=True, blank=True, db_index=True
    )
    value = models.DecimalField("Valor", max_digits=20, decimal_places=2)
    start_date = models.DateField("Data de início", db_index=True)
    end_date = models.DateField("Data final", db_index=True)
    excluded = models.BooleanField("Excluído?", default=False)
    files = GenericRelation(File)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Câmara de Vereadores - Contrato"
        verbose_name_plural = "Câmara de Vereadores - Contratos"
        get_latest_by = "start_date"
        ordering = ["-start_date"]

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
    published_at = models.DateField(
        "Publicado em", null=True, blank=True, db_index=True
    )
    phase = models.CharField("Fase", max_length=20, choices=PHASE, db_index=True)
    phase_code = models.CharField(
        "Código da fase", max_length=20, null=True, blank=True, db_index=True
    )
    company_or_person = models.TextField(
        "Empresa ou pessoa", null=True, blank=True, db_index=True
    )
    value = models.DecimalField("Valor", max_digits=20, decimal_places=2)
    number = models.CharField(
        "Número", max_length=50, null=True, blank=True, db_index=True
    )
    document = models.CharField(
        "CNPJ ou CPF", max_length=50, null=True, blank=True, db_index=True
    )
    date = models.DateField("Data", db_index=True)
    process_number = models.CharField(
        "Número do processo", max_length=50, null=True, blank=True, db_index=True
    )
    summary = models.TextField("Descrição", null=True, blank=True, db_index=True)
    legal_status = models.CharField(
        "Natureza", max_length=200, null=True, blank=True, db_index=True
    )
    function = models.CharField(
        "Função", max_length=50, null=True, blank=True, db_index=True
    )
    subfunction = models.CharField(
        "Subfunção", max_length=50, null=True, blank=True, db_index=True
    )
    resource = models.CharField(
        "Fonte", max_length=200, null=True, blank=True, db_index=True
    )
    subgroup = models.CharField(
        "Subgrupos", max_length=100, null=True, blank=True, db_index=True
    )
    group = models.CharField(
        "Grupo", max_length=100, null=True, blank=True, db_index=True
    )
    budget_unit = models.PositiveIntegerField("Unidade orçamentária", default=101)
    modality = models.CharField(
        "Modalidade",
        max_length=50,
        null=True,
        blank=True,
        choices=EXPENSE_MODALITIES,
        db_index=True,
    )
    excluded = models.BooleanField("Excluído?", default=False)
    external_file_code = models.CharField(
        "Código do arquivo (externo)",
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
    )
    external_file_line = models.CharField(
        "Linha do arquivo (externo)",
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Câmara de Vereadores - Despesa"
        verbose_name_plural = "Câmara de Vereadores - Despesas"
        get_latest_by = "date"
        ordering = ["-date"]

    def __repr__(self):
        return f"{self.date} {self.phase} {self.company_or_person} {self.value}"

    def __str__(self):
        return f"{self.date} {self.phase} {self.company_or_person} {self.value}"


class CityCouncilMinute(DatasetMixin):
    date = models.DateField("Data", db_index=True)
    title = models.CharField(
        "Título", max_length=300, null=True, blank=True, db_index=True
    )
    event_type = models.CharField(
        "Tipo de evento",
        max_length=30,
        choices=CITY_COUNCIL_EVENT_TYPE,
        null=True,
        blank=True,
        db_index=True,
    )
    files = GenericRelation(File)

    class Meta:
        verbose_name = "Câmara de Vereadores - Atas"
        verbose_name_plural = "Câmara de Vereadores - Atas"
        get_latest_by = "date"
        ordering = ["-date"]

    def __repr__(self):
        return f"{self.date} {self.title}"

    def __str__(self):
        return f"{self.date} {self.title}"


class Gazette(DatasetMixin):
    POWER_TYPE = (
        ("executivo", "Poder Executivo"),
        ("legislativo", "Poder Legislativo"),
    )
    date = models.DateField("Data", null=True, db_index=True)
    power = models.CharField("Poder", max_length=25, choices=POWER_TYPE, db_index=True)
    year_and_edition = models.CharField("Ano e edição", max_length=100, db_index=True)
    is_legacy = models.BooleanField("É do site antigo?", default=False)
    files = GenericRelation(File)

    class Meta:
        verbose_name = "Diário Oficial"
        verbose_name_plural = "Diários Oficiais"
        get_latest_by = "date"
        ordering = [F("date").desc(nulls_last=True)]

    def __repr__(self):
        return f"{self.date} {self.power} {self.year_and_edition}"

    def __str__(self):
        return f"{self.date} {self.power} {self.year_and_edition}"


class GazetteEvent(DatasetMixin):
    gazette = models.ForeignKey(
        Gazette, on_delete=models.CASCADE, related_name="events"
    )
    title = models.CharField(
        "Título", max_length=300, null=True, blank=True, db_index=True
    )
    secretariat = models.CharField(
        "Secretaria", max_length=100, null=True, blank=True, db_index=True
    )
    summary = models.TextField("Sumário", null=True, blank=True, db_index=True)
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
    session_at = models.DateTimeField("Sessão Data / Horário", null=True, db_index=True)
    public_agency = models.CharField("Órgão", max_length=200, db_index=True)
    description = models.TextField("Descrição", null=True, blank=True, db_index=True)
    modality = models.CharField(
        "Modalidade",
        max_length=60,
        choices=BID_MODALITIES,
        null=True,
        blank=True,
        db_index=True,
    )
    codes = models.CharField("Códigos", max_length=300, db_index=True)
    files = GenericRelation(File)

    class Meta:
        verbose_name = "Prefeitura - Licitação"
        verbose_name_plural = "Prefeitura - Licitações"
        get_latest_by = "session_at"
        ordering = [F("session_at").desc(nulls_last=True)]

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
        CityHallBid, on_delete=models.CASCADE, related_name="events"
    )
    published_at = models.DateTimeField("Publicado em", null=True)
    summary = models.TextField("Descrição", null=True, blank=True, db_index=True)
    files = GenericRelation(File)

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
    external_code = models.CharField("Código externo", max_length=10, db_index=True)
    modality = models.CharField(
        "Modalidade",
        max_length=60,
        choices=BID_MODALITIES,
        null=True,
        blank=True,
        db_index=True,
    )
    code = models.CharField("Código da licitação", max_length=15, db_index=True)
    code_type = models.CharField(
        "Código do tipo da licitação", max_length=15, db_index=True
    )
    description = models.TextField("Descrição (objeto)", db_index=True)
    session_at = models.DateTimeField("Sessão Data / Horário", null=True, db_index=True)
    excluded = models.BooleanField("Excluído?", default=False)
    files = GenericRelation(File)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Câmara de Vereadores - Licitação"
        verbose_name_plural = "Câmara de Vereadores - Licitações"
        get_latest_by = "session_at"
        ordering = [F("session_at").desc(nulls_last=True)]

    def __repr__(self):
        model_name = self._meta.verbose_name
        return f"{model_name} {self.session_at} {self.code} {self.code_type}"

    def __str__(self):
        model_name = self._meta.verbose_name
        return f"{model_name} {self.session_at} {self.code} {self.code_type}"


class CityCouncilRevenue(DatasetMixin):
    external_code = models.PositiveIntegerField(
        "Código externo", db_index=True, unique=True
    )
    budget_unit = models.PositiveIntegerField("Unidade gestora", default=101)
    published_at = models.DateField("Publicado em", null=True, db_index=True)
    registered_at = models.DateField("Registrado em", null=True, db_index=True)
    revenue_type = models.CharField(
        "Tipo da receita", choices=REVENUE_TYPES, max_length=20, db_index=True
    )
    modality = models.CharField("Modalidade", max_length=60, null=True, blank=True)
    description = models.TextField("Descrição")
    value = models.DecimalField("Valor", max_digits=20, decimal_places=2)
    resource = models.CharField(
        "Fonte", max_length=200, null=True, blank=True, default="prefeitura"
    )
    legal_status = models.CharField(
        "Natureza", max_length=200, null=True, blank=True, db_index=True
    )
    destination = models.CharField("Destinação", max_length=200, null=True, blank=True)
    excluded = models.BooleanField("Excluído?", default=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Câmara de Vereadores - Receita"
        verbose_name_plural = "Câmara de Vereadores - Receitas"
        get_latest_by = "published_at"
        ordering = [F("published_at").desc(nulls_last=True)]

    def __repr__(self):
        model_name = self._meta.verbose_name
        return f"{model_name} {self.published_at} {self.modality} {self.value}"

    def __str__(self):
        model_name = self._meta.verbose_name
        return f"{model_name} {self.published_at} {self.modality} {self.value}"


class SyncInformation(models.Model):
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    date = models.DateField("Data alvo")
    source = models.CharField(
        "Fonte", choices=SYNC_SOURCE, max_length=20, db_index=True
    )
    succeed = models.BooleanField("Concluída com sucesso?", null=True)
    response = models.JSONField("Resposta", null=True)

    class Meta:
        verbose_name = "Sincronização"
        verbose_name_plural = "Sincronizações"
        ordering = ["-created_at"]

    def __repr__(self):
        return f"{self.source} {self.created_at} {self.date}"

    def __str__(self):
        created_at_label = self.created_at.strftime("%d-%m-%Y")
        date_label = self.date.strftime("%d-%m-%Y")
        return f"{self.source.title()} em {created_at_label} para {date_label}"


class TCMBADocument(DatasetMixin):
    class PeriodCategory(models.TextChoices):
        MONTHLY = "mensal", "Mensal"
        YEARLY = "anual", "Anual"

    year = models.PositiveIntegerField("Ano", db_index=True)
    month = models.PositiveIntegerField("Mês", null=True, db_index=True)
    period = models.CharField(
        "Periodicidade", max_length=10, choices=PeriodCategory.choices, db_index=True
    )
    category = models.CharField("Categoria", max_length=200, db_index=True)
    unit = models.CharField("Unidade", max_length=100, db_index=True)
    inserted_at = models.DateField("Inserido em", null=True)
    inserted_by = models.CharField("Inserido por", max_length=50, null=True, blank=True)
    original_filename = models.CharField("Nome do arquivo", max_length=200)

    files = GenericRelation(File)

    class Meta:
        verbose_name = "TCM-BA - Documento"
        verbose_name_plural = "TCM-BA - Documentos"
        get_latest_by = "inserted_at"
        ordering = [F("year").desc(), F("month").desc()]

    def __repr__(self):
        time = self.year
        if self.period == self.PeriodCategory.MONTHLY:
            time = f"{self.month}/{self.year}"
        return f"{time} - {self.original_filename} - {self.unit}"

    def __str__(self):
        return self.original_filename
