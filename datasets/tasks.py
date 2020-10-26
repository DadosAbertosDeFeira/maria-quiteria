import os
from datetime import date, datetime, timedelta
from logging import info
from pathlib import Path

import requests
from datasets.services import get_s3_client
from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.exceptions import ImproperlyConfigured
from dotenv import find_dotenv, load_dotenv
from dramatiq import actor, get_broker, set_broker
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.brokers.stub import StubBroker
from tika import parser

# Esse bloco (feio) faz com que esse módulo funcione dentro ou fora do Django
try:
    from datasets.models import (
        CityCouncilBid,
        CityCouncilContract,
        CityCouncilExpense,
        CityCouncilRevenue,
        File,
    )
except ImproperlyConfigured:
    import configurations

    os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    load_dotenv(find_dotenv())
    configurations.setup()
    from datasets.models import (
        CityCouncilBid,
        CityCouncilContract,
        CityCouncilExpense,
        CityCouncilRevenue,
        File,
    )

# models precisam ser importados depois das configurações
# para manter compatibilidade com o scraper
from datasets.adapters import (  # noqa isort:skip
    to_citycouncil_bid,
    to_citycouncil_contract,
    to_citycouncil_expense,
    to_citycouncil_revenue,
)


if os.getenv("DJANGO_CONFIGURATION") != "Prod":
    broker = StubBroker()
    broker.emit_after("process_boot")
else:
    broker = RabbitmqBroker(url=settings.BROKER_URL)
set_broker(broker)
client = get_s3_client(settings)


class WebserviceException(Exception):
    pass


@actor(max_retries=5)
def content_from_file(file_pk=None, path=None, keep_file=True):
    if not any([file_pk, path]):
        raise Exception("Ou `file_pk` ou `path` devem ser informados.")

    a_file = None
    if file_pk:
        a_file = File.objects.get(pk=file_pk)

        if a_file.content is not None:
            return a_file.content

        path = client.download_file(a_file.s3_file_path)
        keep_file = False

    if not Path(path).exists():
        info(f"Arquivo {path} não encontrado.")
        return

    raw = parser.from_file(path)

    if not keep_file:
        Path(path).unlink()

    if a_file:
        a_file.content = raw["content"]
        a_file.save()

    return raw["content"]


@actor(max_retries=5)
def backup_file(file_id):
    try:
        file_obj = File.objects.get(pk=file_id, s3_url__isnull=True)
    except File.DoesNotExist:
        info(f"O arquivo ({file_id}) não existe ou já possui backup.")
        return

    model_name = file_obj.content_object._meta.model_name
    relative_file_path = (
        f"{model_name}/{file_obj.created_at.year}/"
        f"{file_obj.created_at.month}/{file_obj.created_at.day}/"
    )

    s3_url, s3_file_path = client.upload_file(
        file_obj.url, relative_file_path, prefix=file_obj.checksum
    )
    file_obj.s3_file_path = s3_file_path
    file_obj.s3_url = s3_url
    file_obj.save()

    return s3_url


@actor(max_retries=5)
def get_city_council_updates():
    """Solicita atualizações ao webservice da Câmara."""
    yesterday = date.today() - timedelta(days=1)  # formato aaaa-mm-dd
    response = requests.post(
        settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT,
        data={
            "data": yesterday.strftime("%Y-%m-%d"),
            "token": settings.CITY_COUNCIL_WEBSERVICE_TOKEN,
        },
        headers={"User-Agent": "Maria Quitéria"},
    )
    response.raise_for_status()
    response = response.json()
    if response.get("erro"):
        raise WebserviceException(response["erro"])
    return response


@actor(max_retries=0)
def distribute_city_council_objects_to_sync(payload):
    """Recebe o payload e dispara uma task para cada registro.

    O webservice da Câmara retorna uma lista de ações (inserção,
    atualização e deleção) e os registros que sofreram cada uma
    delas. Essa task executa cada uma de maneira separada para que,
    caso tenham algum erro, possam ser tratados de maneira separada.
    """
    action_methods = {
        "inclusoesContrato": add_citycouncil_contract,
        "alteracoesContrato": update_citycouncil_contract,
        "exclusoesContrato": remove_citycouncil_contract,
        "inclusoesLicitacao": add_citycouncil_bid,
        "alteracoesLicitacao": update_citycouncil_bid,
        "exclusoesLicitacao": remove_citycouncil_bid,
        "inclusoesReceita": add_citycouncil_revenue,
        "alteracoesReceita": update_citycouncil_revenue,
        "exclusoesReceita": remove_citycouncil_revenue,
        "inclusoesDespesa": add_citycouncil_expense,
        "alteracoesDespesa": update_citycouncil_expense,
        "exclusoesDespesa": remove_citycouncil_expense,
    }
    broker = get_broker()
    for action_name, records in payload.items():
        task = action_methods.get(action_name)
        for record in records:
            broker.enqueue(task.message(record))


def save_citycouncil_files(files, object, url_key):
    if not files:
        return
    content_type = get_content_type_for_model(object)
    from datasets.management.commands._file import save_file

    if files:
        for file_ in files:
            url = f"{settings.CITY_COUNCIL_WEBSERVICE}{file_[url_key]}"
            save_file(url, content_type, object.pk)


@actor
def add_citycouncil_bid(record):
    new_item = to_citycouncil_bid(record)
    new_item["crawled_at"] = datetime.now()
    new_item["crawled_from"] = settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT
    bid = CityCouncilBid.objects.create(**new_item)
    save_citycouncil_files(record.get("arquivos"), bid, "caminhoArqLic")

    return bid


@actor
def update_citycouncil_bid(record):
    bid = CityCouncilBid.objects.get(external_code=record["codLic"])
    updated_item = to_citycouncil_bid(record)
    for key, value in updated_item.items():
        setattr(bid, key, value)
    bid.save()
    save_citycouncil_files(record.get("arquivos"), bid, "caminhoArqLic")

    return bid


@actor
def remove_citycouncil_bid(record):
    CityCouncilBid.objects.filter(external_code=record["codLic"]).update(excluded=True)


@actor
def add_citycouncil_contract(record):
    new_item = to_citycouncil_contract(record)
    new_item["crawled_at"] = datetime.now()
    new_item["crawled_from"] = settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT
    contract = CityCouncilContract.objects.create(**new_item)
    save_citycouncil_files(record.get("arquivos"), contract, "caminho")

    return contract


@actor
def update_citycouncil_contract(record):
    contract = CityCouncilContract.objects.get(external_code=record["codCon"])
    updated_item = to_citycouncil_contract(record)
    for key, value in updated_item.items():
        setattr(contract, key, value)
    contract.save()
    save_citycouncil_files(record.get("arquivos"), contract, "caminho")

    return contract


@actor
def remove_citycouncil_contract(record):
    CityCouncilContract.objects.filter(external_code=record["codCon"]).update(
        excluded=True
    )


@actor
def add_citycouncil_revenue(record):
    new_item = to_citycouncil_revenue(record)
    new_item["crawled_at"] = datetime.now()
    new_item["crawled_from"] = settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT
    return CityCouncilRevenue.objects.create(**new_item)


@actor
def update_citycouncil_revenue(record):
    revenue = CityCouncilRevenue.objects.get(external_code=record["codLinha"])
    updated_item = to_citycouncil_revenue(record)
    for key, value in updated_item.items():
        setattr(revenue, key, value)
    revenue.save()
    return revenue


@actor
def remove_citycouncil_revenue(record):
    CityCouncilRevenue.objects.filter(external_code=record["codLinha"]).update(
        excluded=True
    )


@actor
def add_citycouncil_expense(record):
    new_item = to_citycouncil_expense(record)
    new_item["crawled_at"] = datetime.now()
    new_item["crawled_from"] = settings.CITY_COUNCIL_WEBSERVICE_ENDPOINT
    return CityCouncilExpense.objects.create(**new_item)


@actor
def update_citycouncil_expense(record):
    expense = CityCouncilExpense.objects.get(
        external_file_code=record["codArquivo"], external_file_line=record["codLinha"],
    )
    updated_item = to_citycouncil_expense(record)
    for key, value in updated_item.items():
        setattr(expense, key, value)
    expense.save()
    return expense


@actor
def remove_citycouncil_expense(record):
    CityCouncilExpense.objects.filter(
        external_file_code=record["codArquivo"], external_file_line=record["codLinha"],
    ).update(excluded=True)
