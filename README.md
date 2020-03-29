# Maria Quitéria

![](https://gitlab.com/anapaulagomes/maria-quiteria/badges/master/pipeline.svg)

Um projeto para libertar dados do município de [Feira de Santana](https://pt.wikipedia.org/wiki/Feira_de_Santana).

Não sabe quem foi [Maria Quitéria](https://pt.wikipedia.org/wiki/Maria_Quit%C3%A9ria)?

## Dados

| Base de dados | Fonte | Descrição        | Coleta          | Banco de dados | Download |
| ------------- | ------------- | ------------- |:-------------:|:-----:|:-----:|
| Agenda (`citycouncil.py`) | Câmara Municipal | Coleta agenda da Câmara Municipal. | :heavy_check_mark: | :heavy_check_mark: | 🔜 |
| Lista de Presença (`citycouncil.py`) | Câmara Municipal | Coleta assiduidade dos vereadores da Câmara Municipal. | :heavy_check_mark: | :heavy_check_mark: | 🔜 |
| Contratos (`cityhall.py`) | Prefeitura | Contratos realizados pela prefeitura entre 2016 e 2017. | :heavy_check_mark: | 🔜 | [Kaggle](https://www.kaggle.com/anapaulagomes/contratos-da-prefeitura-de-feira-de-santana) |
| Diário Oficial (`gazette.py`) | Prefeitura/Câmara de Vereadores | Diário oficial do executivo e legislativo desde 2015. | :heavy_check_mark: | :heavy_check_mark: | [Kaggle](https://www.kaggle.com/anapaulagomes/dirios-oficiais-de-feira-de-santana)  |
| Diário Oficial (legado - antes de 2015) (`gazette.py`) | Prefeitura | Leis e decretos entre 1999 e 2015. | :heavy_check_mark: | :heavy_check_mark: | [Kaggle](https://www.kaggle.com/anapaulagomes/dirios-oficiais-de-feira-de-santana-at-2015) |
| Licitações (`cityhall.py`) | Prefeitura | Licitações realizadas pela prefeitura desde 2015. | :heavy_check_mark: | 🔜 | [Kaggle](https://www.kaggle.com/anapaulagomes/licitaes-da-prefeitura-de-feira-de-santana) |
| Pagamentos (`cityhall.py`) | Prefeitura | Pagamentos realizados pela prefeitura desde 2010. | :heavy_check_mark: | 🔜 | [Kaggle](https://www.kaggle.com/anapaulagomes/pagamentos-da-prefeitura-de-feira-de-santana) |

## Coleta

Esse projeto usa [Scrapy](https://docs.scrapy.org/en/latest/) para a coleta de dados
e [Django](https://www.djangoproject.com/) para o _backend_.

### Configurando seu ambiente

* Instale as dependências

Para rodar esse projeto localmente, instale as dependências:

```bash
pip install -r dev_requirements.txt
```

* Postgres

Esse projeto usa o Postgres. Para rodar o banco de dados local, crie um
banco de dados com o nome `mariaquiteria`. Depois basta aplicar as `migrations`:

```
python manage.py migrate
```

* Docker (alpha)

Se você não quiser instalar todas as dependencias, você pode [instalar](https://docs.docker.com/install/) e usar o Docker. 
Para isso, você precisa criar um `.env` como abaixo:

```
KEEP_FILES=True
SPIDERMON_TELEGRAM_FAKE=True
SPIDERMON_SENTRY_FAKE=True
DJANGO_SETTINGS_MODULE=core.settings
DJANGO_CONFIGURATION=Prod
DJANGO_SECRET_KEY=dont-tell-anybody
POSTGRES_PASSWORD=maria1792
```

Depois (somente na primeira vez):

`docker-compose build` para construir a imagem

`docker-compose up` para executar a imagem

`docker-compose exec web ./manage.py migrate` para criar as tabelas no banco

`docker-compose exec web ./manage.py createsuperuser` para criar um usuario `admin`

E por fim `docker-compose exec web ./manage.py collectstatic` para processar e mover os arquivos estáticos. 

Reinicie os containers: `docker-compose restart` 

Nas próximas vezes, basta executar os containers: `docker-compose up` e acesse [localhost:8000/admin](http://localhost:8000/admin)


Para a acessar o banco depois com seu cliente preferido, basta usar os seguintes dados:

```
User: postgres
Password: a senha que você definiu
Database: postgres
Host: localhost
```

Para 

**IMPORTANTE**: o uso do docker (ainda) não faz a instalação do Apache Tika


* Java

Nesse projeto utilizamos o [Apache Tika](https://tika.apache.org/download.html)
para extrair o conteúdo dos arquivos de licitações, contratos e outros.
Para tê-lo funcionando com esse projeto você precisa apenas do Java +7
instalado na sua máquina (pode ser a JRE mesmo).

### Rodando os spiders

No diretório `scraper` você poderá encontrar os _spiders_ responsáveis pela
coleta dos dados. Para entender melhor como eles funcionam, dê uma olhada
na documentação do [scrapy](https://docs.scrapy.org/).

Para executar um _spider_, execute:

```
scrapy crawl cityhall_payments
scrapy crawl cityhall_payments -a start_from_date=03/01/2020
```

Para salvar os dados de um _spider_ em um arquivo:

```
scrapy crawl cityhall_payments -o pagamentos.json
```

Você pode substituir `json` por outros formatos como `csv`.


### Salvando dados da coleta no banco de dados

Para executar os _spiders_ e salvar os itens no banco de dados, execute:

```
python manage.py crawl
```

Nota: estamos migrando do comando `runner.py` para `crawl`, então pode acontecer
de nem todos os _spiders_ estarem disponíveis no comando novo.
