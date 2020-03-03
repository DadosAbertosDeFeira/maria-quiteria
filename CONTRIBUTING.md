# Guia de contribuição

Ficamos muito felizes que você está lendo este guia de contribuição, sempre precisamos
de pessoas voluntárias que acreditem na ideia e queiram contribuir com o projeto.

Se você ainda não fez isso, junte-se também a nós [nosso grupo aberto do Telegram](https://t.me/joinchat/DRT0JBcy-RUk2GJZCnH3Fg)
e participe das discussões. Não hesite em nos procurar para tirar todas as suas dúvidas.

## Antes de começar

Aqui estão alguns recursos importantes que você deve estar ciente antes de começar:

- [Manual de dados abertos para desenvolvedores](https://www.w3c.br/pub/Materiais/PublicacoesW3C/manual_dados_abertos_desenvolvedores_web.pdf)
te explicará um pouco sobre o que são e os principais conceitos por trás dos dados abertos.

- Nossos [projetos](https://github.com/DadosAbertosDeFeira/maria-quiteria/projects),
são um conjunto de funcionalidades e melhorias que queremos desenvolver nesse repositório.
Caso não tenha nada que seja a sua praia, você pode dar uma olhada nos
[projetos gerais](https://github.com/orgs/DadosAbertosDeFeira/projects) do projeto.

- No [nosso Trello](https://trello.com/b/E8v20MFs/dados-abertos-de-feira) você pode
acompanhar o que a comunidade em geral vem trabalhando. Lá você encontrá coisas desde
fotografia até pedidos de acesso a informação.

Os detalhes de como instalar e executar este projeto podem ser encontrados no
[`README.md`](https://github.com/DadosAbertosDeFeira/maria-quiteria/blob/master/README.md).

## Reportando bugs

Você encontrou um bug?

Esta seção irá te guiar sobre como você deve agir para reportar um Bug no Maria Quitéria.
Seguir estas etapas ajuda os mantenedores do projeto e a comunidade a entender o que
aconteceu, como reproduzir o erro e encontrar a solução.

- Bugs são rastreados através de [_issues_ no GitHub](https://guides.github.com/features/issues/), verifique que nenhuma _issue_ foi criada por outro usuário reportando o mesmo erro.
- Crie uma issue explicando o problema e adicionando novas informações detalhadas que ajudem os mantenedores do projeto a reproduzir o problema

## Sugerindo melhorias

Esta seção irá te guiar sobre como sugerir melhorias ao Maria Quiteria, incluindo novas funcionalidades. Quando está criando uma sugestão de melhoria, por favor inclua o máximo de detalhes possíveis.

- Discuta sobre a sua sugestão em nosso [grupo no Telegram](https://t.me/joinchat/DRT0JBcy-RUk2GJZCnH3Fg) com outros participantes e mantenedores do projeto
- Sugestões de melhoria são rastreados através de [_issue_](https://guides.github.com/features/issues/) e [_pull requests_](https://guides.github.com/activities/hello-world/#pr) no GitHub, verifique que nenhuma _issue_ ou _pull request_ foi criada por outro usuário com a mesma sugestão.
- Crie sua issue, com linguagem clara, e com o máximo de detalhes explicando todas as suas sugestões de melhoria para o repositório.

## Criando pull requests

Os processos aqui descritos possuem diversos objetivos:

1. Manter a qualidade do Maria Quitéria
2. Consertar problemas que são importantes para os usuários
3. Engajar a comunidade a trabalhar pelo Maria Quitéria
4. Permitir a sustentabilidade do sistema de revisão de contribuições pelos mantenedores

Siga as seguintes etapas para ter a sua contribuição neste repositório consideradas:

- Use o tempo presente ("Adiciona funcionalidade" e não "Adicionada a funcionalidade")
- Atualize o `README.md` com os detalhes da mudança caso esta inclua uma nova base de dados ou um novo comando na CLI
- Quando necessários, adicione comentários e testes para as novas funcionalidades implementadas

### O básico do GitHub

1. Dê um fork neste repositório

Ao lado direito da página inicial do repositório há um botão escrito Fork.

2. Clone o fork do seu repositório

```console
$ git clone http://github.com/<SEU-USERNAME-NO-GITHUB>/maria-quiteria.git
```

3. Crie um branch com a funcionalidade

```console
$ git checkout -b <NOVA-FUNCIONALIDADE>
```

4. Faça o que você faz de melhor

Agora é a sua hora de brilhar e escrever um bom código que irá fazer este projeto ficar em outro nível

5. Dê um commit de suas mudanças

```console
$ git commit -m 'Minha excelente contribuição'
```

6. Dê um push da sua branch no seu fork

```console
$ git push origin <NOVA-FUNCIONALIDADE>
```

7. Crie um novo Pull Request

A partir da página do seu fork clique no botão para abrir uma nova pull request.
