# Maria Quitéria

Um projeto para libertar dados do município de [Feira de Santana](https://pt.wikipedia.org/wiki/Feira_de_Santana).

## Scraper

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
