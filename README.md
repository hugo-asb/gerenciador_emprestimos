# Desafio Gerenciador de Empréstimos

## Desafio

Este projeto implementa um sistema que permite que usuários gerenciem empréstimos, onde ele pode inseri-los e os respectivos pagamentos. Também é possível visualizá-los por completo ou somente o saldo devedor. A autenticação foi feita via token, sendo que os usuários são criados por um script, que deve ser executado para utilizar a aplicação.

O cálculo do saldo devedor é feito utilizando [juros compostos](https://duckduckgo.com/?q=juros%20compostos&ia=web), adicionando também o [Imposto sobre Operações Financeiras (IOF)](https://duckduckgo.com/?q=imposto%20sobre%20opera%C3%A7%C3%B5es%20financeiras%20opera%C3%A7%C3%A3o%20de%20cr%C3%A9dito), cuja taxa fixa e alíquota diária atuais estavam em 0,38% e 0,0082%, respectivamente.

Foram utilizadas as bibliotecas [Django](https://www.djangoproject.com/) e [Django REST Framework](https://www.django-rest-framework.org/) para construção da API. O banco de dados escolhido foi o [PostgreSQL](https://www.postgresql.org/) e para gerar o relatório de cobertura de testes foi usado o [Coverage](https://coverage.readthedocs.io/en/7.4.4/). A criação dos contêineres, tanto da aplicação como do banco de dados, é feita através do [Docker](https://www.docker.com/) e do [Docker Compose](https://docs.docker.com/compose/)

## Instalação

Após clonar o repositório do projeto, navegue para a pasta onde se encontram os arquivos `Dockerfile` e `docker-compose.yml` e utilize o seguinte comando para criar e executar os contêineres:

```
docker compose up --build
```

Caso já exista uma build, use o comando:

```
docker compose up
```

Se for necessário executar somente o contêiner do banco de dados em segundo plano, utilize:

```
docker compose up -d db
```

A aplicação é acessada no endereço [http://0.0.0.0:8000/](http://0.0.0.0:8000/).

### Criação dos usuários

Para ter acesso às funcionalidades, primeiro é preciso criar os usuários no banco de dados. Com os contêineres rodando, ainda no diretório do passo de instalação, execute o seguinte comando:

```
docker compose exec django ./manage.py create_users_script
```

Dessa forma, dois usuários são criados: um com permissões de administrador e outro sem, que podem ser usados para acessar as funcionalidades da aplicação.

## Utilizando a aplicação

### Autenticação

O acesso aos métodos da aplicação é restrito apenas para usuários autenticados, sendo que a autenticação é feita via token. Para obtê-lo, é necessário fazer uma requisição `POST` no endpoint `/api/users/login/`, passando as credenciais dos usuários que foram criados anteriormente, que, para um usuário sem privilégios de administrador, são:

```
{
	"username":  "generated-user",
	"password":  "user-password"
}
```

Já as credenciais do usuário com privilégios de administrador são:

```
{
	"username":  "generated-admin",
	"password":  "admin-password"
}
```

A resposta estará no seguinte formato:

```
{
	"token":  "your_generated_token"
}
```

Com isso, o cabeçalho das próximas requisições deve conter esse token no campo `Authorization` com o valor `Token your_generated_token`.

Caso as requisições não tenham um token válido, o código de status das respostas será `401`.

### Métodos para gerenciar empréstimos (Loan)

#### POST

Para cadastrar um novo empréstimo, deve-se fazer uma requisição `POST` para o endpoint `/api/loans/`, com o corpo da requisição na seguinte forma:

```
{
	"nominal_value": "valor_do_emprestimo",
	"interest_rate": "taxa_de_juros_mensal",
	"bank": "banco",
	"maturity_date": "data_de_vencimento(yyyy-mm-dd)"
}
```

Caso todos os campos sejam válidos, a código de status da resposta será `201` e o corpo será do empréstimo cadastrado. Caso contrário, o código vai ser `400` e o corpo trará a descrição do erro.

#### GET

#### Buscar por ID

Para buscar um empréstimo específico, deve se fazer uma requisição `GET` para o endpoint `/api/loans/<id>/`, no qual `<id>` é o identificador do empréstimo.

Caso o empréstimo buscado exista e pertença ao usuário que o está pesquisando, o código de status da resposta será `200` e o corpo será o empréstimo cadastrado.

Caso o empréstimo buscado não exista, o código de status da resposta será `404`. Já se o empréstimo não pertencer ao usuário o código de status da resposta será `403`. Em ambos os casos o corpo da resposta será a mensagem de erro.

#### Listar todos os empréstimos

Para buscar todos os empréstimos, deve se fazer uma requisição `GET` para o endpoint `/api/loans/list/`.

O código de status da resposta será `200` e o corpo da resposta terá a lista de todos os empréstimos cadastrados e, caso não haja nenhum, a lista será vazia.

Por ser uma listagem com paginação, por padrão, a resposta trará os últimos 10 empréstimos. Para aumentar ou diminuir essa quantidade, deve-se modificar o tamanho da página por parâmetros na URL, da seguinte forma:

```
/api/loans/list/?page_size=<size>&page=<page>
```

Substitua `<size>` pela quantidade de empréstimos que devem ser buscados por página (o valor máximo permitido é 100). Também é possível navegar por elas através desses parâmetros, bastando trocar `<page>` pela página que se deseja acessar. Caso a página acessada não exista, o código de status da resposta será `404` e o corpo conterá a mensagem de erro. Ambos parâmetros são opcionais.

A resposta da requisição também terá as seguintes propriedades adicionais:

- _Links_: possui outras duas propriedades:
  - _next_: endereço para a próxima página.
  - _previous_: endereço da página anterior.
- _count_: quantidade total de empréstimos cadastrados.
- _results_: lista com os empréstimos da página.

#### Buscar o saldo devedor

Para buscar o saldo devedor de um empréstimo específico, deve se fazer uma requisição `GET` para o endpoint `/api/loans/<id>/outstanding_balance/`, no qual `<id>` é o identificador do empréstimo.

Caso o empréstimo buscado exista e pertença ao usuário que o está pesquisando, o código de status da resposta será `200` e o corpo terá o identificador do usuário e do empréstimo, além do saldo devedor.

Caso o empréstimo buscado não exista, o código de status da resposta será `404`. Já se o empréstimo não pertencer ao usuário o código de status da resposta será `403`. Em ambos os casos o corpo da resposta será a mensagem de erro.

#### PATCH

Para modificar um empréstimo, deve-se fazer uma requisição `PATCH` para o endpoint `/api/loans/<id>/`, no qual `<id>` é o identificador do empréstimo, com o corpo da requisição na seguinte forma (somente a taxa de juros e valor nominal podem ser modificados):

```
{
	"interest_rate":  "taxa_de_juros",
	"nominal_value":  "valor_nominal"
}
```

Caso todos os campos sejam válidos, a código de status da resposta será `200` e o corpo será do empréstimo atualizado. Caso contrário, o código vai ser `400` e o corpo trará a descrição do erro.

Se o empréstimo buscado não existir, o código de status da resposta será `404`. Já se o empréstimo não pertencer ao usuário o código de status da resposta será `403`. Em ambos os casos o corpo da resposta será a mensagem de erro.

#### DELETE

Para deletar um empréstimo, deve-se fazer uma requisição `DELETE` para o endpoint `/api/loans/<id>/`, no qual `<id>` é o identificador do empréstimo.

Se o empréstimo existe e pertence ao usuário, o código de status da resposta será `204`. Caso o empréstimo buscado não exista, o código será `404`, e se o empréstimo não pertencer ao usuário, será `403`. Em ambos os casos o corpo da resposta será a mensagem de erro.

### Métodos para gerenciar pagamentos (Payment)

#### POST

Para cadastrar um novo pagamento, deve-se fazer uma requisição `POST` para o endpoint `/api/payments/`, com o corpo da requisição na seguinte forma:

```
{
	"value": "valor_do_pagamento",
	"date": "data_do_pagamento(yyyy-mm-dd)",
	"loan": "id_do_emprestimo"
}
```

Caso todos os campos sejam válidos, a código de status da resposta será `201` e o corpo será do pagamento cadastrado. Caso contrário, o código vai ser `400` e o corpo trará a descrição do erro. Se o campo `loan` for de um empréstimo inexistente, o código retornado será `404`.

#### GET

#### Buscar por ID

Para buscar um pagamento específico, deve se fazer uma requisição `GET` para o endpoint `/api/payments/<id>/`, no qual `<id>` é o identificador do pagamento.

Caso o pagamento buscado exista e pertença ao usuário que o está pesquisando, o código de status da resposta será `200` e o corpo será o pagamento cadastrado.

Caso o pagamento buscado não exista, o código de status da resposta será `404`. Já se o pagamento não pertencer ao usuário o código de status da resposta será `403`. Em ambos os casos o corpo da resposta será a mensagem de erro.

#### Listar todos os pagamentos

Para buscar todos os pagamentos, deve se fazer uma requisição `GET` para o endpoint `/api/payments/list_all/`.

O código de status da resposta será `200` e o corpo da resposta terá a lista de todos os pagamentos cadastrados e, caso não haja nenhum, a lista será vazia.

Por ser uma listagem com paginação, por padrão, a resposta trará os últimos 10 pagamentos. Para aumentar ou diminuir essa quantidade, deve-se modificar o tamanho da página por parâmetros na URL, da seguinte forma:

```
/api/payments/list_all/?page_size=<size>&page=<page>
```

Substitua `<size>` pela quantidade de pagamentos que devem ser buscados por página (o valor máximo permitido é 100). Também é possível navegar por elas através desses parâmetros, bastando trocar `<page>` pela página que se deseja acessar. Caso a página acessada não exista, o código de status da resposta será `404` e o corpo conterá a mensagem de erro. Ambos parâmetros são opcionais.

A resposta da requisição também terá as seguintes propriedades adicionais:

- _Links_: possui outras duas propriedades:
  - _next_: endereço para a próxima página.
  - _previous_: endereço da página anterior.
- _count_: quantidade total de empréstimos cadastrados.
- _results_: lista com os empréstimos da página.

#### Listar todos os pagamentos de um empréstimo

Para buscar todos os pagamentos referentes a um empréstimo específico, deve se fazer uma requisição `GET` para o endpoint `/api/payments/list/<id>/`, no qual `<id>` é o identificador do **empréstimo**.

O código de status da resposta será `200` e o corpo da resposta terá a lista de todos os pagamentos cadastrados para esse empréstimo e, caso não haja nenhum, a lista será vazia. A paginação funciona de forma análoga ao do tópico acima, porém a URL ficaria na forma:

```
/api/payments/list/?page_size=<size>&page=<page>
```

Caso o empréstimo buscado não exista, o código de status da resposta será `404`. Já se o empréstimo não pertencer ao usuário o código de status da resposta será `403`. Em ambos os casos o corpo da resposta será a mensagem de erro.

#### DELETE

Para deletar um pagamento, deve-se fazer uma requisição `DELETE` para o endpoint `/api/payments/<id>/`, no qual `<id>` é o identificador do pagamento.

Se o pagamento existe e pertence ao usuário, o código de status da resposta será `204`. Caso o pagamento buscado não exista, o código será `404`, e se não pertencer ao usuário, será `403`. Em ambos os casos o corpo da resposta será a mensagem de erro.

### Testes

Para executar todos os testes, utilize o seguinte comando, ainda no diretório do passo de instalação:

```
docker compose exec django ./manage.py test
```

Para executar os testes de um _app_ específico, substitua `<app>` pelo _app_ a ser testado:

```
docker compose exec django ./manage.py test <app>
```

Para executar os testes e gerar um relatório de cobertura, utilize:

```
docker compose exec django coverage run ./manage.py test
```

Para visualizar o relatório que foi gerado:

```
docker compose exec django coverage report
```
