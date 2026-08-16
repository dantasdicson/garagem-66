# Garagem 66

Sistema web para gerenciamento de uma oficina virtual de motocicletas. O projeto possui uma API em Django REST Framework e um frontend React.

## Pré-requisitos

- Python 3.11 ou superior
- Node.js 20 ou superior
- Docker e Docker Compose (para o PostgreSQL local)

## Preparar o backend

1. Crie o arquivo de ambiente a partir do exemplo:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Crie e ative um ambiente virtual Python.

3. Instale as dependências:

   ```powershell
   pip install -r requirements/development.txt
   ```

4. Inicie o PostgreSQL:

   ```powershell
   docker compose up -d db
   ```

5. Gere/aplique as migrations e inicie a API:

   ```powershell
   cd backend
   python manage.py migrate
   python manage.py runserver
   ```

A API estará disponível em `http://127.0.0.1:8000/` e o admin em `http://127.0.0.1:8000/admin/`.

## Autenticação da API

Crie o primeiro administrador pelo Django:

```powershell
python manage.py createsuperuser
```

Escolha o perfil `ADMINISTRADOR`. Para obter um token de acesso, envie `username` e `password` para `POST /api/auth/token/`. Use o `access` recebido no cabeçalho `Authorization: Bearer <token>`. A renovação é feita em `POST /api/auth/token/refresh/` com o `refresh`.

O cadastro de um cliente pela API cria automaticamente seu usuário. O login é o CPF sem pontuação e a senha inicial é a data de nascimento no formato `DDMMAAAA`. O acesso ao restante da API fica bloqueado até a senha ser alterada em:

```text
POST /api/usuarios/alterar-senha/
```

Os dados do usuário autenticado podem ser consultados em `GET /api/usuarios/me/`.

O telefone do cliente é opcional. Quando informado, deve conter DDD e 10 ou 11 dígitos; entradas com máscara ou prefixo `+55` são aceitas e armazenadas no formato `(DD) 99999-9999` ou `(DD) 9999-9999`.

Após trocar a senha inicial, o perfil cliente pode consultar somente seu próprio cadastro, suas motocicletas, ordens de serviço, orçamentos e históricos. O filtro é aplicado no servidor: tentar consultar o identificador de um registro pertencente a outro cliente retorna `404`. O cliente não pode criar ou alterar dados operacionais; sua escrita permanece limitada à aprovação ou recusa do próprio orçamento.

## Preparar o frontend

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

O frontend será servido normalmente em `http://localhost:5173/`.

O frontend já possui login JWT, restauração da sessão, renovação automática do token, troca obrigatória da senha inicial, rotas protegidas e menus por perfil. Configure `VITE_API_URL` com a URL base da API, incluindo `/api`. O arquivo `frontend/vercel.json` garante que links internos funcionem quando a aplicação React for publicada na Vercel.

Administrador e atendente já possuem telas para listar, cadastrar e editar clientes e motocicletas. O cadastro da motocicleta seleciona o proprietário existente. O cliente possui uma visualização somente leitura de suas próprias motocicletas, apoiada também pelos filtros de segurança do backend.

## Publicação para apresentação

O arquivo `render.yaml` provisiona a API Django e o PostgreSQL no Render. A inicialização executa migrations e o comando idempotente `criar_dados_demo`, portanto as contas de apresentação já existem quando o serviço fica disponível.

No Render, informe nas variáveis solicitadas pelo Blueprint:

```text
DJANGO_CORS_ALLOWED_ORIGINS=https://SEU-FRONTEND.vercel.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://SEU-FRONTEND.vercel.app
```

Na Vercel, importe o mesmo repositório, use `frontend` como Root Directory e configure:

```text
VITE_API_URL=https://SUA-API.onrender.com/api
```

Contas demonstrativas (senha comum `Garagem66@Demo`):

```text
Administrador: admin.demo
Atendente: atendente.demo
Mecânico: mecanico.demo
Cliente: 52998224725
```

Essas contas são exclusivamente fictícias. Não use dados pessoais no banco de apresentação e remova ou troque as credenciais depois da avaliação.

## Variáveis de ambiente

Consulte `.env.example`. Em produção, defina `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, hosts permitidos, origens CORS e todas as credenciais do PostgreSQL no ambiente de deploy.

## Estrutura

- `backend/apps/usuarios`: autenticação e perfis.
- `backend/apps/oficina`: clientes, motocicletas, entradas e ordens de serviço.
- `backend/apps/estoque`: peças e requisições relacionadas às ordens de serviço.
- `frontend`: aplicação React estruturada para evoluir por páginas, componentes e serviços.

## Regras já implementadas

- Uma peça utilizada fica vinculada à ordem de serviço por meio de `ItemPeca`.
- Ao registrar o item, sua quantidade é descontada do estoque de forma transacional.
- Quantidades superiores ao saldo disponível são recusadas.
- Ao excluir o item, a quantidade retorna ao estoque.
- O mecânico pode solicitar uma peça somente para uma ordem de serviço atribuída a ele.
- Somente o administrador pode aprovar ou recusar uma requisição pendente.

As decisões de requisição utilizam:

```text
POST /api/estoque/requisicoes-peca/{id}/aprovar/
POST /api/estoque/requisicoes-peca/{id}/recusar/
```

O fluxo de orçamento utiliza:

```text
POST /api/oficina/orcamentos/
POST /api/oficina/orcamentos/{id}/aprovar/
POST /api/oficina/orcamentos/{id}/recusar/
```

Administrador ou atendente emite o orçamento. Somente o cliente proprietário pode aprovar ou recusar. A aprovação move a OS para `EM_EXECUCAO`; a recusa encerra a OS como `CONCLUIDA_NAO_APROVADA`.

Serviços e peças previstos são cadastrados separadamente dos itens realmente executados:

```text
POST /api/oficina/orcamento-servicos/
POST /api/oficina/orcamento-pecas/
```

Os itens previstos recalculam os totais do orçamento, mas não alteram o estoque. A baixa ocorre apenas quando um `ItemPeca` é registrado na ordem de serviço durante a execução.

A entrada da motocicleta é registrada de forma transacional em:

```text
POST /api/oficina/entradas-veiculo/
```

O corpo da requisição inclui `itens_checklist`, `avarias` e `acessorios`. Todos os nove itens do checklist são obrigatórios e não podem se repetir. Pneus exigem percentual entre 0 e 100; os demais itens exigem estado. Se qualquer parte for inválida, nenhuma informação da entrada é gravada. Uma entrada válida move a ordem de `ABERTA` para `AGUARDANDO_ORCAMENTO`.

Serviços executados e peças utilizadas somente podem ser registrados quando a ordem estiver em `EM_EXECUCAO` ou `AGUARDANDO_PECAS` e possuir orçamento `APROVADO`. Um mecânico somente pode trabalhar nas ordens atribuídas a ele; administrador e atendente podem acompanhar e operar todas as ordens.

Cada transição da ordem registra status anterior, novo status, responsável, data e observação. O histórico é somente leitura e pode ser filtrado pela ordem:

```text
GET /api/oficina/historico-status-ordens/?ordem_servico={id}
```

O campo `status` da ordem não pode ser alterado diretamente pela API. As transições dos fluxos de entrada e orçamento usam o serviço central de status para preservar a auditoria.

## Fluxo da ordem de serviço

As transições permitidas são:

```text
ABERTA -> AGUARDANDO_ORCAMENTO ou AGUARDANDO_APROVACAO
AGUARDANDO_ORCAMENTO -> AGUARDANDO_APROVACAO
AGUARDANDO_APROVACAO -> EM_EXECUCAO ou CONCLUIDA_NAO_APROVADA
EM_EXECUCAO -> AGUARDANDO_PECAS ou CONCLUIDA
AGUARDANDO_PECAS -> EM_EXECUCAO ou CONCLUIDA
CONCLUIDA -> EM_EXECUCAO (reabertura administrativa)
CONCLUIDA_NAO_APROVADA -> estado terminal
```

Endpoints operacionais:

```text
POST /api/oficina/ordens-servico/{id}/aguardar_pecas/
POST /api/oficina/ordens-servico/{id}/retomar_execucao/
POST /api/oficina/ordens-servico/{id}/concluir/
POST /api/oficina/ordens-servico/{id}/reabrir/
```

Administrador, atendente e o mecânico atribuído podem pausar, retomar e concluir. Somente o administrador pode reabrir uma ordem concluída, sendo obrigatória uma justificativa. A conclusão preenche `concluida_em`; a reabertura limpa essa data.
