# Especificação da API de Tarefas

## 1. Objetivo

A API de Tarefas será uma aplicação REST simples construída com FastAPI e
SQLite. Ela servirá como projeto de exemplo para o Codex analisar, documentar
e publicar no Notion por meio do MCP oficial.

A implementação deverá privilegiar contratos claros, validações explícitas,
descrições OpenAPI e comportamentos fáceis de testar e documentar.

## 2. Escopo funcional

A API deverá permitir:

- criar uma tarefa;
- listar tarefas;
- filtrar tarefas por status;
- consultar uma tarefa por identificador;
- atualizar uma tarefa parcial ou integralmente;
- excluir uma tarefa.

Não fazem parte desta primeira versão:

- autenticação e autorização;
- usuários ou responsáveis pelas tarefas;
- categorias, etiquetas ou subtarefas;
- paginação;
- ordenação configurável;
- exclusão lógica;
- histórico de alterações;
- notificações;
- API assíncrona ou processamento em segundo plano.

## 3. Convenções gerais

### Formato

- As requisições e respostas deverão utilizar JSON.
- Datas e horários deverão utilizar ISO 8601 em UTC.
- O identificador da tarefa deverá ser um número inteiro positivo.
- Os caminhos deverão usar substantivos no plural.
- A API não deverá retornar detalhes internos do banco de dados ou stack
  traces.

### Caminho base

Os endpoints da primeira versão deverão usar o prefixo:

```text
/api/v1
```

### Content-Type

Requisições com corpo deverão utilizar:

```http
Content-Type: application/json
```

## 4. Modelo de domínio

### Status da tarefa

O campo `status` deverá aceitar somente:

| Valor | Significado |
|---|---|
| `pending` | A tarefa ainda não foi iniciada. |
| `in_progress` | A tarefa está em execução. |
| `completed` | A tarefa foi concluída. |

O valor padrão para uma nova tarefa será `pending`.

### Tarefa

| Campo | Tipo | Obrigatório | Regras |
|---|---|---:|---|
| `id` | integer | resposta | Gerado pelo banco, maior que zero. |
| `title` | string | sim | Entre 3 e 120 caracteres após remover espaços externos. |
| `description` | string ou null | não | No máximo 1000 caracteres; padrão `null`. |
| `status` | enum | não | Padrão `pending`. |
| `created_at` | datetime | resposta | Gerado na criação, em UTC. |
| `updated_at` | datetime | resposta | Gerado na criação e alterado em cada atualização. |

## 5. Schemas da API

### `TaskCreate`

Usado para criar uma tarefa.

```json
{
  "title": "Documentar API de tarefas",
  "description": "Gerar a documentação técnica da API.",
  "status": "pending"
}
```

Campos aceitos:

- `title`: obrigatório;
- `description`: opcional;
- `status`: opcional.

Campos desconhecidos deverão ser rejeitados.

### `TaskUpdate`

Usado para atualizar uma tarefa. Todos os campos serão opcionais, mas a
requisição deverá informar pelo menos um deles.

```json
{
  "status": "in_progress"
}
```

Campos aceitos:

- `title`;
- `description`;
- `status`.

O valor `null` será permitido somente para `description`. `title` e `status`
não poderão ser anulados.

Campos desconhecidos deverão ser rejeitados.

### `TaskResponse`

Representação completa retornada pela API.

```json
{
  "id": 1,
  "title": "Documentar API de tarefas",
  "description": "Gerar a documentação técnica da API.",
  "status": "pending",
  "created_at": "2026-06-24T14:00:00Z",
  "updated_at": "2026-06-24T14:00:00Z"
}
```

### `ErrorResponse`

Formato dos erros controlados pela aplicação:

```json
{
  "detail": "Task not found"
}
```

Erros automáticos de validação do FastAPI poderão manter o formato padrão
HTTP 422 do framework.

## 6. Endpoints

### Verificar saúde da aplicação

```http
GET /health
```

Confirma que a aplicação está em execução. Esse endpoint não utilizará o
prefixo `/api/v1`.

#### Resposta de sucesso

Status: `200 OK`

```json
{
  "status": "ok"
}
```

### Criar tarefa

```http
POST /api/v1/tasks
```

Cria uma nova tarefa.

#### Corpo

Schema: `TaskCreate`

#### Resposta de sucesso

Status: `201 Created`

Schema: `TaskResponse`

O cabeçalho `Location` deverá apontar para:

```text
/api/v1/tasks/{id}
```

#### Possíveis erros

- `422 Unprocessable Entity`: corpo inválido.

### Listar tarefas

```http
GET /api/v1/tasks
```

Retorna todas as tarefas cadastradas, ordenadas por `id` em ordem crescente.

#### Parâmetro de query

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `status` | enum | não | Retorna somente tarefas com o status informado. |

Exemplo:

```http
GET /api/v1/tasks?status=pending
```

#### Resposta de sucesso

Status: `200 OK`

Schema: lista de `TaskResponse`.

Quando não houver tarefas, deverá retornar:

```json
[]
```

#### Possíveis erros

- `422 Unprocessable Entity`: status inválido.

### Consultar tarefa

```http
GET /api/v1/tasks/{task_id}
```

Retorna uma tarefa pelo identificador.

#### Parâmetro de rota

| Nome | Tipo | Regra |
|---|---|---|
| `task_id` | integer | Deve ser maior que zero. |

#### Resposta de sucesso

Status: `200 OK`

Schema: `TaskResponse`.

#### Possíveis erros

- `404 Not Found`: tarefa inexistente;
- `422 Unprocessable Entity`: identificador inválido.

Resposta para tarefa inexistente:

```json
{
  "detail": "Task not found"
}
```

### Atualizar tarefa

```http
PATCH /api/v1/tasks/{task_id}
```

Atualiza somente os campos enviados pelo cliente.

#### Corpo

Schema: `TaskUpdate`

#### Regras

- campos ausentes deverão manter o valor atual;
- `updated_at` deverá ser atualizado quando a operação for concluída;
- o envio de um objeto vazio deverá ser rejeitado;
- as mesmas validações da criação deverão ser aplicadas aos campos enviados.

#### Resposta de sucesso

Status: `200 OK`

Schema: `TaskResponse` com os valores atualizados.

#### Possíveis erros

- `404 Not Found`: tarefa inexistente;
- `422 Unprocessable Entity`: identificador ou corpo inválido.

### Substituir tarefa

```http
PUT /api/v1/tasks/{task_id}
```

Substitui os campos editáveis de uma tarefa existente.

#### Corpo

Schema: `TaskCreate`

O cliente deverá enviar `title`, podendo também informar `description` e
`status`. Campos opcionais omitidos voltarão aos seus valores padrão:

- `description`: `null`;
- `status`: `pending`.

#### Resposta de sucesso

Status: `200 OK`

Schema: `TaskResponse`.

#### Possíveis erros

- `404 Not Found`: tarefa inexistente;
- `422 Unprocessable Entity`: identificador ou corpo inválido.

### Excluir tarefa

```http
DELETE /api/v1/tasks/{task_id}
```

Exclui definitivamente uma tarefa.

#### Resposta de sucesso

Status: `204 No Content`

A resposta não deverá possuir corpo.

#### Possíveis erros

- `404 Not Found`: tarefa inexistente;
- `422 Unprocessable Entity`: identificador inválido.

## 7. Resumo dos contratos

| Método | Caminho | Sucesso | Corpo de entrada | Corpo de saída |
|---|---|---:|---|---|
| GET | `/health` | 200 | — | Status da aplicação |
| POST | `/api/v1/tasks` | 201 | `TaskCreate` | `TaskResponse` |
| GET | `/api/v1/tasks` | 200 | — | Lista de `TaskResponse` |
| GET | `/api/v1/tasks/{task_id}` | 200 | — | `TaskResponse` |
| PATCH | `/api/v1/tasks/{task_id}` | 200 | `TaskUpdate` | `TaskResponse` |
| PUT | `/api/v1/tasks/{task_id}` | 200 | `TaskCreate` | `TaskResponse` |
| DELETE | `/api/v1/tasks/{task_id}` | 204 | — | Sem corpo |

## 8. Persistência

A aplicação deverá utilizar SQLite.

### Tabela `tasks`

| Coluna | Tipo lógico | Restrições |
|---|---|---|
| `id` | integer | Chave primária e autoincremento. |
| `title` | varchar(120) | Não nulo. |
| `description` | text | Nulo permitido. |
| `status` | varchar | Não nulo. |
| `created_at` | datetime | Não nulo. |
| `updated_at` | datetime | Não nulo. |

O banco deverá preservar os dados entre reinicializações da aplicação.

Para simplificar o MVP, a criação da tabela poderá acontecer automaticamente
na inicialização. Uma ferramenta de migração de banco de dados não será
obrigatória nesta versão.

Durante os testes, deverá ser usado um banco separado e descartável para não
alterar os dados do ambiente local.

## 9. Regras de validação

- Espaços no início e no final de `title` deverão ser removidos.
- Um título composto apenas por espaços deverá ser rejeitado.
- Após a normalização, `title` deverá conter entre 3 e 120 caracteres.
- `description` deverá possuir no máximo 1000 caracteres.
- `status` deverá corresponder exatamente a um valor definido no enum.
- Identificadores de rota deverão ser maiores que zero.
- Objetos com propriedades não definidas nos schemas deverão ser rejeitados.
- O corpo vazio de uma atualização parcial deverá ser rejeitado.

## 10. Tratamento de erros

A aplicação deverá:

- retornar `404` para tarefas inexistentes;
- retornar `422` para falhas de validação;
- retornar `500` somente para falhas inesperadas;
- registrar internamente erros inesperados;
- não expor consultas SQL, caminhos locais, credenciais ou stack traces;
- usar mensagens consistentes para o mesmo tipo de falha.

Não deverá haver diferença entre consultar, atualizar ou excluir uma tarefa
inexistente: todos esses casos retornarão `404` com `Task not found`.

## 11. OpenAPI e documentação automática

A aplicação deverá configurar no FastAPI:

- título da API;
- descrição;
- versão `1.0.0`;
- informações de cada tag;
- resumo e descrição de cada endpoint;
- `response_model` de cada resposta com corpo;
- códigos de status de sucesso e erro;
- descrição dos parâmetros;
- exemplos nos schemas principais.

As rotas de documentação deverão permanecer disponíveis:

| Recurso | Caminho |
|---|---|
| Swagger UI | `/docs` |
| ReDoc | `/redoc` |
| Especificação OpenAPI | `/openapi.json` |

Os endpoints de tarefas deverão usar a tag `Tasks`, e o endpoint de saúde
deverá usar a tag `Health`.

## 12. Organização sugerida

A implementação deverá separar, no mínimo:

- inicialização e configuração da aplicação;
- modelos e schemas;
- acesso ao banco de dados;
- rotas de tarefas;
- regras ou serviços de tarefa;
- testes.

As rotas não deverão conter detalhes desnecessários de configuração do SQLite.
A sessão ou conexão com o banco deverá ser fornecida por dependência do
FastAPI e encerrada corretamente após cada requisição.

## 13. Testes obrigatórios

Os testes deverão cobrir:

### Saúde

- resposta `200` de `/health`;
- corpo `{"status": "ok"}`.

### Criação

- criação com todos os campos;
- criação somente com título e aplicação dos valores padrão;
- retorno do cabeçalho `Location`;
- rejeição de título curto, longo, vazio ou composto por espaços;
- rejeição de status inválido;
- rejeição de campos desconhecidos.

### Listagem

- lista vazia;
- retorno de várias tarefas em ordem crescente de `id`;
- filtro por cada status;
- filtro sem resultados;
- rejeição de status inválido.

### Consulta

- consulta de tarefa existente;
- retorno `404` para tarefa inexistente;
- rejeição de identificador menor ou igual a zero.

### Atualização parcial

- atualização isolada de cada campo;
- preservação dos campos não enviados;
- remoção da descrição com `null`;
- alteração de `updated_at`;
- rejeição de objeto vazio;
- retorno `404` para tarefa inexistente.

### Substituição

- substituição de todos os campos editáveis;
- aplicação dos padrões para campos opcionais omitidos;
- retorno `404` para tarefa inexistente.

### Exclusão

- exclusão com resposta `204` e sem corpo;
- impossibilidade de consultar a tarefa depois da exclusão;
- retorno `404` ao excluir tarefa inexistente.

### Persistência e contrato

- isolamento do banco utilizado nos testes;
- presença de todos os endpoints em `/openapi.json`;
- compatibilidade dos schemas OpenAPI com os corpos retornados.

## 14. Critérios de conclusão

A API estará pronta para ser analisada pelo Codex quando:

- todos os endpoints especificados estiverem implementados;
- os dados persistirem em SQLite;
- os testes obrigatórios estiverem aprovados;
- o OpenAPI descrever corretamente entradas, respostas e erros;
- Swagger UI e ReDoc estiverem acessíveis;
- os exemplos não contiverem dados sensíveis;
- não existirem comportamentos públicos relevantes fora desta especificação.

## 15. Decisões técnicas consolidadas

- A API utilizará o estilo REST.
- A primeira versão será identificada pelo prefixo `/api/v1`.
- A persistência será feita em SQLite.
- O status será representado por um enum textual.
- `PATCH` fará atualização parcial.
- `PUT` fará substituição dos campos editáveis.
- A exclusão será definitiva.
- Erros de validação manterão o padrão HTTP 422 do FastAPI.
- A API não terá autenticação no MVP.
