# Plano incremental de entrega da API de Tarefas

Este plano divide a implementação descrita em
[`especificacao-api-tarefas.md`](./especificacao-api-tarefas.md) em partes
pequenas. Cada parte deve terminar com a aplicação executável e pode ser feita
em uma sessão separada.

## Como usar este plano

- Execute as partes na ordem indicada.
- Marque os itens concluídos nas listas de verificação.
- Ao terminar uma parte, rode os testes existentes antes de seguir.
- Faça, se possível, um commit por parte. Assim, cada avanço fica fácil de
  revisar ou desfazer.
- Considere a parte concluída somente quando todos os itens de seu critério de
  conclusão forem atendidos.

## Visão geral

| Parte | Entrega | Resultado verificável |
|---:|---|---|
| 1 | Base do projeto | Aplicação inicia e `/health` responde corretamente |
| 2 | Schemas e validações | Entradas inválidas são rejeitadas com HTTP 422 |
| 3 | SQLite | Tabela é criada e a conexão é fornecida às rotas |
| 4 | Criar tarefa | `POST /api/v1/tasks` persiste uma tarefa |
| 5 | Listar e consultar | Tarefas podem ser listadas, filtradas e consultadas |
| 6 | Atualizar e substituir | `PATCH` e `PUT` alteram tarefas corretamente |
| 7 | Excluir tarefa | `DELETE` remove uma tarefa definitivamente |
| 8 | Erros e OpenAPI | Contratos e erros estão documentados e consistentes |
| 9 | Testes e revisão final | Suíte obrigatória passa e a API está pronta para análise |

## Parte 1 — Base da aplicação e endpoint de saúde

**Status: concluída.**

Objetivo: deixar a estrutura mínima da aplicação correta antes de implementar
as regras de tarefas.

- [x] Definir as dependências do projeto, incluindo FastAPI, servidor ASGI e
  ferramentas de teste.
- [x] Configurar o `FastAPI` com título, descrição e versão `1.0.0`.
- [x] Organizar a inicialização da aplicação separadamente das rotas.
- [x] Corrigir o prefixo das tarefas para `/api/v1`.
- [x] Criar `GET /health` sem o prefixo `/api/v1`.
- [x] Retornar `200` com `{"status": "ok"}` no endpoint de saúde.
- [x] Manter `/docs`, `/redoc` e `/openapi.json` acessíveis.
- [x] Criar os primeiros testes para a saúde da aplicação.

Critério de conclusão: a aplicação inicia sem erros, o teste de saúde passa e
o endpoint aparece no OpenAPI com a tag `Health`.

Commit sugerido: `feat: configurar base da API e health check`

## Parte 2 — Schemas e validações

Objetivo: consolidar os contratos de entrada e saída antes de acessar o banco.

- [ ] Manter o enum com `pending`, `in_progress` e `completed`.
- [ ] Criar ou ajustar o schema `TaskCreate`.
- [ ] Criar o schema `TaskUpdate`, com todos os campos opcionais.
- [ ] Rejeitar um `TaskUpdate` sem nenhum campo informado.
- [ ] Criar o schema `TaskResponse`.
- [ ] Remover espaços externos do título.
- [ ] Validar o título normalizado entre 3 e 120 caracteres.
- [ ] Limitar a descrição a 1000 caracteres.
- [ ] Permitir `null` apenas para `description` durante atualizações.
- [ ] Rejeitar campos desconhecidos em entradas.
- [ ] Adicionar exemplos aos schemas principais.
- [ ] Testar as validações dos schemas isoladamente ou pelas rotas.

Critério de conclusão: todos os contratos da seção 5 da especificação existem
e entradas inválidas retornam HTTP 422 sem chegar à persistência.

Commit sugerido: `feat: definir schemas e validacoes de tarefas`

## Parte 3 — Persistência com SQLite

Objetivo: substituir o armazenamento em memória por persistência local.

- [ ] Escolher e configurar a biblioteca de acesso ao SQLite.
- [ ] Criar a tabela `tasks` com todas as colunas especificadas.
- [ ] Criar a tabela automaticamente na inicialização da aplicação.
- [ ] Implementar uma dependência do FastAPI que forneça a conexão ou sessão.
- [ ] Garantir o encerramento da conexão após cada requisição.
- [ ] Separar o acesso ao banco das rotas.
- [ ] Configurar um banco temporário e isolado para os testes.
- [ ] Confirmar que dados locais sobrevivem à reinicialização da aplicação.

Critério de conclusão: a tabela é criada automaticamente, uma operação feita
no banco permanece após reiniciar a aplicação e os testes não alteram o banco
local.

Commit sugerido: `feat: adicionar persistencia sqlite`

## Parte 4 — Criação de tarefas

Objetivo: entregar o primeiro fluxo funcional completo.

- [ ] Implementar `POST /api/v1/tasks`.
- [ ] Persistir título, descrição, status e datas em UTC.
- [ ] Aplicar `pending` e `null` como valores padrão.
- [ ] Retornar o schema completo com HTTP 201.
- [ ] Incluir o cabeçalho `Location: /api/v1/tasks/{id}`.
- [ ] Adicionar resumo, descrição, respostas e tag `Tasks` ao OpenAPI.
- [ ] Testar criação completa, criação mínima, valores padrão e `Location`.
- [ ] Testar títulos inválidos, status inválido e campos desconhecidos.

Critério de conclusão: uma tarefa válida é gravada no SQLite e todos os casos
de criação da seção 13 da especificação passam.

Commit sugerido: `feat: implementar criacao de tarefas`

## Parte 5 — Listagem e consulta

Objetivo: permitir a leitura das tarefas persistidas.

- [ ] Implementar `GET /api/v1/tasks`.
- [ ] Ordenar a listagem por `id` crescente.
- [ ] Retornar uma lista vazia quando não houver registros.
- [ ] Implementar o filtro opcional por `status`.
- [ ] Rejeitar um status de filtro inválido com HTTP 422.
- [ ] Implementar `GET /api/v1/tasks/{task_id}`.
- [ ] Validar que `task_id` é maior que zero.
- [ ] Retornar HTTP 404 com `{"detail": "Task not found"}` quando necessário.
- [ ] Cobrir listagem, filtros, consulta, 404 e identificador inválido em testes.

Critério de conclusão: todas as tarefas criadas podem ser listadas e
consultadas, e todos os casos de leitura da seção 13 passam.

Commit sugerido: `feat: implementar consulta e listagem de tarefas`

## Parte 6 — Atualização parcial e substituição

Objetivo: completar as duas formas de edição previstas no contrato.

- [ ] Implementar `PATCH /api/v1/tasks/{task_id}`.
- [ ] Alterar somente os campos enviados no `PATCH`.
- [ ] Permitir remover a descrição enviando `null`.
- [ ] Rejeitar corpo vazio no `PATCH`.
- [ ] Implementar `PUT /api/v1/tasks/{task_id}`.
- [ ] Exigir o título no `PUT`.
- [ ] Restaurar `description=null` e `status=pending` quando omitidos no `PUT`.
- [ ] Atualizar `updated_at` em UTC nas duas operações.
- [ ] Preservar `id` e `created_at` nas duas operações.
- [ ] Retornar o mesmo erro 404 usado na consulta.
- [ ] Cobrir os cenários de atualização e substituição com testes.

Critério de conclusão: os testes obrigatórios de atualização parcial e
substituição passam, incluindo padrões, preservação de campos e datas.

Commit sugerido: `feat: implementar atualizacao de tarefas`

## Parte 7 — Exclusão

Objetivo: fechar o ciclo CRUD.

- [ ] Implementar `DELETE /api/v1/tasks/{task_id}`.
- [ ] Remover o registro definitivamente do SQLite.
- [ ] Retornar HTTP 204 sem corpo.
- [ ] Validar que `task_id` é maior que zero.
- [ ] Retornar o erro 404 padronizado para tarefa inexistente.
- [ ] Testar exclusão, consulta após exclusão, 404 e identificador inválido.

Critério de conclusão: uma tarefa excluída não pode mais ser consultada e a
resposta 204 não possui corpo.

Commit sugerido: `feat: implementar exclusao de tarefas`

## Parte 8 — Tratamento de erros e documentação OpenAPI

Objetivo: revisar o contrato público depois que todos os fluxos existirem.

- [ ] Padronizar o 404 de consulta, atualização, substituição e exclusão.
- [ ] Declarar no OpenAPI os códigos de sucesso e erros controlados.
- [ ] Garantir que falhas inesperadas sejam registradas sem expor detalhes.
- [ ] Revisar títulos, descrições, tags e parâmetros de todos os endpoints.
- [ ] Declarar `response_model` em todas as respostas com corpo.
- [ ] Conferir os caminhos e schemas gerados em `/openapi.json`.
- [ ] Conferir manualmente Swagger UI e ReDoc.
- [ ] Confirmar que exemplos e mensagens não expõem dados sensíveis.

Critério de conclusão: o OpenAPI representa fielmente todos os endpoints e
nenhuma resposta controlada expõe detalhes internos da aplicação.

Commit sugerido: `docs: completar contratos OpenAPI da API`

## Parte 9 — Suíte completa e preparação para documentação

Objetivo: provar que a entrega atende à especificação e está pronta para o
fluxo de documentação no Notion.

- [ ] Revisar a lista de testes obrigatórios da seção 13 da especificação.
- [ ] Adicionar qualquer cenário obrigatório que ainda esteja sem cobertura.
- [ ] Testar o isolamento do banco de testes.
- [ ] Testar a presença de todos os endpoints no OpenAPI.
- [ ] Testar a compatibilidade entre schemas e respostas reais.
- [ ] Executar a suíte completa a partir de um ambiente limpo.
- [ ] Documentar no README como instalar, executar e testar a API.
- [ ] Remover armazenamento em memória e código provisório remanescente.
- [ ] Revisar os critérios de conclusão da seção 14 da especificação.

Critério de conclusão: a suíte completa passa, a execução está documentada e
todos os critérios da especificação foram conferidos.

Commit sugerido: `test: concluir cobertura e preparar entrega da API`

## Checklist final da entrega

- [ ] `GET /health`
- [ ] `POST /api/v1/tasks`
- [ ] `GET /api/v1/tasks`
- [ ] `GET /api/v1/tasks/{task_id}`
- [ ] `PATCH /api/v1/tasks/{task_id}`
- [ ] `PUT /api/v1/tasks/{task_id}`
- [ ] `DELETE /api/v1/tasks/{task_id}`
- [ ] Persistência real em SQLite
- [ ] Banco de testes separado
- [ ] Validações e erros consistentes
- [ ] OpenAPI, Swagger UI e ReDoc revisados
- [ ] Testes obrigatórios aprovados
- [ ] Instruções de execução e teste no README

Depois desse checklist, a próxima entrega será gerar a prévia da documentação
em `docs/api-tarefas.md`, revisá-la e somente então publicá-la no Notion com
aprovação explícita.
