# Maria Quitéria

![CI](https://github.com/DadosAbertosDeFeira/maria-quiteria/workflows/CI/badge.svg)

Um projeto para libertar dados do município de [Feira de Santana](https://pt.wikipedia.org/wiki/Feira_de_Santana).

Não sabe quem foi [Maria Quitéria](https://pt.wikipedia.org/wiki/Maria_Quit%C3%A9ria)?

## Dados

| Base de dados | Fonte | Descrição        | Coleta          | Banco de dados | Download |
| ------------- | ------------- | ------------- |:-------------:|:-----:|:-----:|
| Agenda (`citycouncil.py`) | Câmara Municipal | Agenda (ordem do dia, homenagens, sessões ordinárias etc) da Câmara Municipal. | :heavy_check_mark: | :heavy_check_mark: | 🔜 |
| Atas das sessões (`citycouncil.py`) | Câmara Municipal | Atas das sessões da Câmara Municipal. | :heavy_check_mark: | :heavy_check_mark: | 🔜 |
| Lista de Presença (`citycouncil.py`) | Câmara Municipal | Assiduidade dos vereadores da Câmara Municipal. | :heavy_check_mark: | :heavy_check_mark: | 🔜 |
| Despesas (`citycouncil.py`) | Câmara Municipal | Gastos realizados pela Câmara Municipal. | :heavy_check_mark: | :heavy_check_mark: | [Kaggle](https://www.kaggle.com/anapaulagomes/despesas-da-cmara-municipal) |
| Contratos (`cityhall.py`) | Prefeitura | Contratos realizados pela prefeitura entre 2016 e 2017. | :heavy_check_mark: | 🔜 | [Kaggle](https://www.kaggle.com/anapaulagomes/contratos-da-prefeitura-de-feira-de-santana) |
| Diário Oficial (`gazette.py`) | Prefeitura/Câmara de Vereadores | Diário oficial do executivo e legislativo desde 2015. | :heavy_check_mark: | :heavy_check_mark: | [Kaggle](https://www.kaggle.com/anapaulagomes/dirios-oficiais-de-feira-de-santana)  |
| Diário Oficial (legado - antes de 2015) (`gazette.py`) | Prefeitura | Leis e decretos entre 1999 e 2015. | :heavy_check_mark: | :heavy_check_mark: | [Kaggle](https://www.kaggle.com/anapaulagomes/dirios-oficiais-de-feira-de-santana-at-2015) |
| Licitações (`cityhall.py`) | Prefeitura | Licitações realizadas pela prefeitura desde 2015. | :heavy_check_mark: | 🔜 | [Kaggle](https://www.kaggle.com/anapaulagomes/licitaes-da-prefeitura-de-feira-de-santana) |
| Pagamentos (`cityhall.py`) | Prefeitura | Pagamentos realizados pela prefeitura desde 2010. | :heavy_check_mark: | 🔜 | [Kaggle](https://www.kaggle.com/anapaulagomes/pagamentos-da-prefeitura-de-feira-de-santana) |

## Contribuindo para o projeto

Contribuições são muito bem-vindas. Veja como contribuir no nosso [Guia de Contribuição](CONTRIBUTING.md).

Toda a comunicação e demais interações do Dados Abertos de Feira estão sujeitas
ao nosso [Código de Conduta](CODE_OF_CONDUCT.md).

## Coleta

Esse projeto usa [Scrapy](https://docs.scrapy.org/en/latest/) para a coleta de dados
e [Django](https://www.djangoproject.com/) para o _backend_.

### Configurando seu ambiente

* Instale as dependências

Para rodar esse projeto localmente, instale as dependências:

```bash
pip install -r dev_requirements.txt
```

* Carregue as variáveis de ambiente

Um exemplo das configurações pode ser encontrado no arquivo `.env.example`
(que pode ser copiado para um arquivo `.env` na raiz do projeto).

* Postgres

Esse projeto usa o Postgres. Para rodar o banco de dados local, crie um
banco de dados com o nome `mariaquiteria`.

Adicione a variável de ambiente `DATABASE_URL` com a url de conexão ao seu Postgres.
Ex: `DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME`

Depois basta aplicar as `migrations`:

```
python manage.py migrate
```

#### Usando Docker

Se você não quiser instalar todas as dependências, você pode instalar o [Docker](https://docs.docker.com/install/) em conjunto com o [Docker Compose](https://docs.docker.com/compose/install/).

Para isso, você precisa criar um `.env` como no `.env.example` da raiz do projeto.

* Executando o projeto no Docker:

1. Iniciando o serviço:

```
make build
```

2. Crie as tabelas no banco:

```
make migrate
```

3. Crie um usuario `admin`:

```
make createsuperuser
```

4. Processe e move arquivos estáticos:

```
make collectstatic
```

5. Executando o serviço:

```
make setup
```

6. Rodando os testes:

```
make test
```

Nas próximas vezes, basta executar os containers: `docker-compose up` e acesse [localhost:8000/admin](http://localhost:8000/admin)


Para a acessar o banco depois com seu cliente preferido, basta usar os seguintes dados:

```
User: postgres
Password: postgres
Database: mariaquiteria
Host: localhost
```

#### Executando os testes

```
make runtests
```

* Admin

Para navegar na admin, primeiro crie um super administrador:
```
python manage.py createsuperuser
```

Depois, rode o servidor com:
```
python manage.py runserver
```

Com as configurações padrão o painel de controle estará acessível pela URL: [`127.0.0.1`](http://127.0.0.1:8000).

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

#### Extraindo o conteúdo dos arquivos ao rodar os spiders

Para incluir o conteúdo dos arquivos nos itens raspados
você deve configurar a variável de ambiente `EXTRACT_FILE_CONTENT_FROM_PIPELINE`
como `True`.

### Salvando dados da coleta no banco de dados

Para executar os _spiders_ e salvar os itens no banco de dados, execute:

```
python manage.py crawl
```

Caso queira passar alguma configuração extra para o Scrapy através
do comando `crawl` você pode adicionar após o parâmetro `--scrapy-args`:

```
./manage.py crawl --scrapy-args '{"LOG_FILE": "test.log"}'
```

#### Serviço de fila e processamento assíncrono

Você pode utilizar ou não um serviço de fila para processamento assíncrono. Isso
é **totalmente** opcional. Essa funcionalidade pode ser utilizada para
extraírmos o conteúdo de PDFs para texto, com o Tika, de maneira assíncrona à
raspagem de dados. Por padrão, essa funcionalidade está ativada, seguindo
a configuração do ambiente de produção.

Para utilizá-la, basta instalar o RabbitMQ. Para essa última parte, temos duas
formas de te ajudar. Basta seguir para a próxima seção.

Caso queira desativar essa funcionalidade, você vai precisar configurar a variável
de ambiente `ASYNC_FILE_PROCESSING` para `False`.

##### Utilizando o Docker para subir o RabbitMQ

Se você não quiser instalar o RabbitMQ, a forma mais prática de ter uma
instância dele rodando é com o [Docker](https://docs.docker.com/install/):

```
docker run -p 5672:5672 rabbitmq
```

Deixe esse processo rodando em uma janela do terminal.
Em outra janela, execute o `dramatiq`:

```
dramatiq datasets.tasks -p3 -v
```

##### Instalando o RabbitMQ localmente

Caso prefira, você pode
[baixar e instalar](https://www.rabbitmq.com/download.html) o RabbitMQ do site
oficial. Feito isso, inicie o serviço em uma janela do terminal e mantenha essa
janela aberta:

```
rabbitmq-server
```
