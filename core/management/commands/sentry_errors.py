import json
import requests

"""
Para corrigir esse erro:
- verificar os arquivos salvos no S3, se existe duplicados
- salvar no banco a url dos arquivos no S3
- start nas background tasks para extrair o conteúdo dos arquivos
- 

Params
[
    datetime.datetime(2020, 11, 24, 3, 1, 51, 316602, tzinfo=<UTC>), 
    datetime.datetime(2020, 11, 24, 3, 8, 13, 403603, tzinfo=<UTC>), 
    'http://www.feiradesantana.ba.gov.br/licitacoes/respostas/5293ata_licitacao_LIC_150-2020_TP_038-2020-_DESERTA_-_perfuração_de_03_(três)_poços_artesianos_no_distrito_de_Humildes.pdf', 
    14, 
    1993, 
    'https://dadosabertosdefeira.s3.eu-central-1.amazonaws.com/maria-quiteria/files/cityhallbidevent/2020/11/24/5293ata_licitacao_LIC_150-2020_TP_038-2020-_DESERTA_-_perfuração_de_03_(três)_poços_artesianos_no_distrito_de_Humildes.pdf',
    'maria-quiteria/files/cityhallbidevent/2020/11/24/5293ata_licitacao_LIC_150-2020_TP_038-2020-_DESERTA_-_perfuração_de_03_(três)_poços_artesianos_no_distrito_de_Humildes.pdf',
    '',
    8365
]
"""

def retrieve_errors(issue_id):
  issue_id = "1685309132"  # FIXME
  endpoint = f"https://sentry.io/api/0/issues/{issue_id}/events/?full=True"
  token = "3cae8c55f58d44b0ada66c746da14c7e1f3994299c33473aa2dd7285f3de637b"  # FIXME
  headers = {"Authorization": f"Bearer {token}"}

  return requests.get(endpoint, headers=headers)


events_from_sentry = json.load(open("sentry-errors-1.json"))
errors = {}
all_params = []

for event in events_from_sentry:
  task_id = None
  from_prod = False
  for tag in event["tags"]:
    if tag["key"] == "environment" and tag["value"] == "Prod":
      from_prod = True
    if tag["key"] == "dramatiq_message_id":
      task_id = tag["value"]
  if task_id and from_prod:
    for entry in event["entries"]:
      if entry["data"].get("values"):
        for value in entry["data"].get("values"):
          if value.get("stacktrace") and value["stacktrace"]["frames"]:
            for frame in value["stacktrace"]["frames"]:
              if frame["vars"].get("params"):
                errors[task_id] = frame["vars"].get("params")
                if frame["vars"].get("params") not in all_params:
                  all_params.append(frame["vars"].get("params"))

for task_id, params in errors.items():
  print("--------------------------")
  print(task_id)
  print(params)

print(len(errors), len(all_params))
# content_from_file(file_pk=None, path=None, keep_file=True)

"""
params[2] =   # url original
params[4] =  # content object id / object_id
params[5] =  # url no s3
params[6] =  # file path no s3
params[-1] = # file pk
"""
