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

### Configurando seu ambiente

Você precisará do [Docker](https://docs.docker.com/install/)
e do [Docker-Compose](https://docs.docker.com/compose/install/) para rodar o projeto.

#### Carregue as variáveis de ambiente

Um exemplo das configurações pode ser encontrado no arquivo `.env.example`,
que deve ser copiado para um arquivo `.env` na raiz do projeto.

Caso queira utilizar um banco de dados diferente basta configurar a variável
de ambiente `DATABASE_URL` em seu `.env`.

#### Instale as dependências e prepare os serviços

```bash
make build
```

O passo anterior vai criar um banco de dados postgres.
Agora, basta aplicar as `migrations`:

```
make migrate
```

### Executando os testes

```
make tests
```

### Acessando o site

Rode o servidor com:
```
make run
```

Com as configurações padrão o painel de controle estará acessível pela URL:
[`localhost:8000`](http://localhost:8000). Veja as bases de dados disponíveis
no nosso painel público [`localhost:8000/painel`](http://localhost:8000/painel).

Para navegar no admin, primeiro crie um super administrador:
```
make createsuperuser
```

### Coletando os dados

Boa parte dos dados que temos vem da raspagem de dados feita por _spiders_.
O comando abaixo vai executar todos os _spiders_ e salvar os itens raspados
no banco de dados:

```
make crawl
```

Durante a coleta e adição ao banco, vamos também tentar extrair o conteúdo
dos arquivos encontrados.

### Rodando os spiders individualmente

No diretório `scraper` você poderá encontrar os _spiders_ responsáveis pela
coleta dos dados. Para entender melhor como eles funcionam, dê uma olhada
na documentação do [scrapy](https://docs.scrapy.org/).

Para rodar um _spider_, execute:

```
SPIDER=citycouncil_agenda make runspider
# ou
SPIDER=citycouncil_agenda START_DATE=03/01/2020 make runspider
```

Para salvar os dados de um _spider_ em um arquivo:

```
docker-compose run --rm web scrapy crawl citycouncil_agenda -o citycouncil_agenda.json
```

Você pode substituir `json` por outros formatos como `csv`.

Caso queira passar alguma configuração extra para o Scrapy através
do comando `crawl` você pode adicionar após o parâmetro `--scrapy-args`:

```
docker-compose run --rm web python manage.py crawl --scrapy-args '{"LOG_FILE": "test.log"}'
```

### API

Sobre acesso a API veja instruções em nossa [Wiki](https://github.com/DadosAbertosDeFeira/maria-quiteria/wiki/API).
