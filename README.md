# Maria Quitéria

![](https://gitlab.com/anapaulagomes/maria-quiteria/badges/master/pipeline.svg)

Um projeto para libertar dados do município de [Feira de Santana](https://pt.wikipedia.org/wiki/Feira_de_Santana).

## Dados

| Base de dados | Fonte | Descrição        | Status           | Download |
| ------------- | ------------- | ------------- |:-------------:|:-----:|
| [Agenda](https://github.com/DadosAbertosDeFeira/maria-quiteria/blob/11453a30ae43a8ddb1421647c98cb104a1977409/scraper/scraper/spiders/citycouncil.py#L4) | Câmara Municipal | Coleta agenda da Câmara Municipal. | ✅ | 🔜 |
| [Contratos](https://github.com/DadosAbertosDeFeira/maria-quiteria/blob/11453a30ae43a8ddb1421647c98cb104a1977409/scraper/scraper/spiders/cityhall.py#L109) | Prefeitura | Contratos realizados pela prefeitura entre 2016 e 2017. | ✅ | 🔜 |
| [Diário Oficial](https://github.com/DadosAbertosDeFeira/maria-quiteria/blob/11453a30ae43a8ddb1421647c98cb104a1977409/scraper/scraper/spiders/gazette.py#L86) | Prefeitura/Câmara de Vereadores | Diário oficial do executivo e legislativo desde 2015. | ✅ | 🔜 |
| [Diário Oficial (legado - antes de 2015)](https://github.com/DadosAbertosDeFeira/maria-quiteria/blob/11453a30ae43a8ddb1421647c98cb104a1977409/scraper/scraper/spiders/gazette.py#L8) | Prefeitura | Leis e decretos entre 1999 e 2015. | ✅ | 🔜 |
| [Licitações](https://github.com/DadosAbertosDeFeira/maria-quiteria/blob/11453a30ae43a8ddb1421647c98cb104a1977409/scraper/scraper/spiders/cityhall.py#L7) | Prefeitura | Licitações realizadas pela prefeitura desde 2015. | ✅ | 🔜 |
| [Pagamentos](https://github.com/DadosAbertosDeFeira/maria-quiteria/blob/11453a30ae43a8ddb1421647c98cb104a1977409/scraper/scraper/spiders/cityhall.py#L193) | Prefeitura | Pagamentos realizados pela prefeitura desde 2010. | ✅ | [Kaggle](https://www.kaggle.com/anapaulagomes/pagamentos-da-prefeitura-de-feira-de-santana) |

## Coleta

Para rodar esse projeto localmente, instale as dependências:

```bash
pip install -r dev_requirements.txt
```

E tenha o [Apache Tika](https://tika.apache.org/download.html) instalado.
Esse projeto vai extrair o texto dos PDFs.

No diretório `scraper` você poderá encontrar os _spiders_ responsáveis pela
coleta dos dados. Para entender melhor como eles funcionam, dê uma olhada
na documentação do [scrapy](https://docs.scrapy.org/).

Para executar um _spider_, execute:

```
cd scraper && scrapy crawl payments
```

Para salvar os dados de um _spider_:

```
cd scraper && scrapy crawl payments -o pagamentos.json
```

Você pode substituir `json` por outros formatos como `csv`.

----

Não sabe quem foi [Maria Quitéria](https://pt.wikipedia.org/wiki/Maria_Quit%C3%A9ria)?
