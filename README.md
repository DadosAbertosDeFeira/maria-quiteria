# Maria Quitéria

Um projeto para libertar dados do município de [Feira de Santana](https://pt.wikipedia.org/wiki/Feira_de_Santana).

## Dados

| Base de dados | Descrição        | Status           | Download |
| ------------- | ------------- |:-------------:| -----:|
| Pagamentos (Prefeitura) | Pagamentos realizados pela prefeitura entre 2010 e 2019. | ✅ | [Kaggle](https://www.kaggle.com/anapaulagomes/pagamentos-da-prefeitura-de-feira-de-santana) |

## Coleta

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
