# Prompt Completo para Implementação do Módulo de Configurações

> Copie e cole o conteúdo abaixo diretamente no chat do Lovable.

---

**AVISO IMPORTANTE: Preserve todo o código e estrutura de arquivos existentes. Não remova, não reescreva e não substitua nenhum arquivo ou rota já criada. Apenas adicione as novas funcionalidades conforme descrito abaixo, integrando-as ao projeto `agenda-aba` existente.**

Preciso que você implemente um **Módulo de Configurações** completo no projeto `agenda-aba`. O objetivo é replicar e adaptar a funcionalidade de configurações do meu outro projeto (`session-stream-desk`), usando os documentos de planejamento que já estão neste repositório como guia.

Leia com atenção todas as instruções e siga a ordem exata das fases. Para cada fase, consulte os arquivos de planejamento correspondentes no repositório (`CONFIG_DATABASE.md`, `CONFIG_API.md`, `CONFIG_IMPLEMENTATION_PLAN.md`).

---

## FASE 1: BANCO DE DADOS

Crie um novo arquivo de migração em `supabase/migrations/` e adicione o SQL para criar e alterar as tabelas conforme especificado no arquivo `CONFIG_DATABASE.md`.

**Instrução:** Implemente o esquema de banco de dados descrito em `CONFIG_DATABASE.md`.

---

## FASE 2: EDGE FUNCTIONS (API)

Crie as Edge Functions no diretório `supabase/functions/` conforme especificado no arquivo `CONFIG_API.md`.

**Instrução:** Implemente as Edge Functions `admin-manage-staff`, `get-role-permissions`, `update-role-permissions` e `admin-manage-franchises` conforme descrito em `CONFIG_API.md`.

---

## FASE 3: FRONTEND

Implemente a interface do usuário seguindo o plano detalhado no arquivo `CONFIG_IMPLEMENTATION_PLAN.md`.

### 3.1. Rota e Página Principal de Configurações

1.  **Adicione a Rota:** No seu arquivo de rotas (`App.tsx`), adicione a rota `/configuracoes` que renderiza um novo componente `Configuracoes.tsx`.
2.  **Adicione o Item de Menu:** No `DashboardLayout.tsx`, adicione um item de menu "Configurações" (ícone `Settings`) que aponta para `/configuracoes`. Este item deve ser visível apenas para usuários com as permissões adequadas (ex: `super_admin`, `franqueado`, `administrador`).
3.  **Crie a Página `Configuracoes.tsx`:** Esta página deve conter um componente `<Tabs>` do shadcn/ui com as seguintes abas: `Cadastros`, `Acessos`, `Documentos`, `Franquias` e `Minha Clínica`.

### 3.2. Aba "Cadastros"

- Dentro da aba "Cadastros", crie um componente de abas aninhado com as seguintes sub-abas: `Pacientes`, `Profissionais`, `Convênios`, `Procedimentos`, `Recursos`, `Equipe` e `Salas`.
- Para cada sub-aba, implemente um CRUD (Criar, Ler, Atualizar, Deletar) completo, reutilizando o estilo e a lógica dos componentes do projeto `session-stream-desk`.
- **Funcionalidade Chave (Convênios e Procedimentos):** Crie uma interface que permita, após cadastrar convênios e procedimentos, vincular um ou mais procedimentos a um convênio, definindo um `valor` específico para aquela combinação.

### 3.3. Aba "Acessos"

- Crie uma interface para gerenciar as permissões de cada papel (`role`).
- A UI deve ter um `Select` para escolher o papel (ex: "Terapeuta", "Recepção").
- Ao selecionar um papel, exiba uma lista de todas as permissões do sistema, agrupadas por categoria (ex: "Pacientes", "Agenda", "Financeiro"), cada uma com um `Checkbox`.
- Ao salvar, as permissões selecionadas para aquele papel devem ser atualizadas no banco de dados através da Edge Function `update-role-permissions`.

### 3.4. Aba "Documentos"

- Implemente uma interface para gerenciar documentos da clínica.
- Deve ser possível criar categorias para os documentos (ex: "Contratos", "Alvarás").
- Deve ser possível fazer o upload de arquivos para cada categoria.
- **Importante:** A funcionalidade de "Configurar Anamnese" do projeto antigo **NÃO** deve ser implementada.

### 3.5. Aba "Franquias"

- Crie uma interface, visível apenas para `super_admin`, para gerenciar as unidades/franquias.
- O formulário de criação/edição deve conter os campos detalhados em `CONFIG_DATABASE.md` (CNPJ, Razão Social, Endereço completo, etc.).
- Utilize um hook `useCepLookup` para preencher automaticamente os campos de endereço a partir do CEP.

### 3.6. Visão Geral (Dashboard)

- Na página principal do dashboard (`/dashboard`), adicione alguns cards de resumo com os principais indicadores de desempenho (KPIs) extraídos dos relatórios.
- **Sugestões de KPIs:**
    - Total de Sessões Realizadas (no mês)
    - Total de Faltas (no mês)
    - Faturamento Total (no mês)
    - Ticket Médio por Atendimento

**Instrução Final:** Comece pela Fase 1 e prossiga em ordem. Consulte os arquivos `.md` no repositório sempre que precisar de detalhes sobre a estrutura de dados, APIs ou plano de implementação.
