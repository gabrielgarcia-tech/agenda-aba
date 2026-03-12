# Plano de Implementação - Módulo de Configurações (v3)

Este documento descreve um plano passo a passo para a implementação do novo Módulo de Configurações no projeto `agenda-aba`.

## Fases

### Fase 1: Backend e Banco de Dados (1 semana)

1.  **[ ] Migração do Banco de Dados:**
    - Criar um novo arquivo de migração SQL no diretório `supabase/migrations/`.
    - Adicionar o SQL para criar as tabelas: `convenios`, `procedimentos`, `convenio_procedimentos`, `recursos_terapeuticos`, `role_permissions`, `document_categories`, `clinic_documents`.
    - Adicionar o SQL para **alterar** a tabela `franchises` (ou `clinics`) e adicionar os novos campos de endereço e contato.
    - Adicionar as políticas de RLS para todas as novas tabelas, garantindo que o acesso seja restrito por `franchise_id`.

2.  **[ ] Edge Functions:**
    - Desenvolver e testar as Edge Functions: `admin-manage-staff`, `get-role-permissions`, `update-role-permissions`, `admin-manage-franchises`.

### Fase 2: Frontend (2 semanas)

1.  **[ ] Hooks de Dados:**
    - Criar novos hooks React Query para interagir com as novas tabelas e Edge Functions (ex: `useConvenios`, `useProcedimentos`, `useRolePermissions`).

2.  **[ ] Estrutura da Página de Configurações:**
    - Criar a rota `/configuracoes` e a página `Configuracoes.tsx`.
    - Adicionar um item "Configurações" no menu lateral (`DashboardLayout.tsx`), visível apenas para usuários com as permissões adequadas (ex: `config:access`, `team:manage`).
    - A página `Configuracoes.tsx` deve usar um componente `<Tabs>` do shadcn/ui para dividir as seções: **Cadastros**, **Acessos**, **Documentos**, **Franquias**, **Minha Clínica**.

3.  **[ ] Aba "Cadastros":**
    - Criar um componente `<Tabs>` aninhado para as sub-seções: Pacientes, Profissionais, Convênios, Procedimentos, Recursos, Equipe, Salas.
    - Reutilizar e adaptar os componentes de lista e diálogo do projeto `session-stream-desk` para cada uma dessas sub-seções.
    - Implementar a lógica para vincular procedimentos a convênios com valores específicos.

4.  **[ ] Aba "Acessos":**
    - Criar a interface para visualizar e editar as permissões de cada `role`.
    - A UI deve mostrar uma lista de papéis e, ao selecionar um, exibir checkboxes para cada permissão disponível no sistema, agrupadas por categoria (Pacientes, Agenda, Financeiro, etc.).
    - O salvamento deve chamar a Edge Function `update-role-permissions`.

5.  **[ ] Aba "Documentos":**
    - Implementar a interface para upload e gerenciamento de documentos, com criação e associação de categorias.
    - **Remover** qualquer funcionalidade relacionada à configuração de Anamnese.
    - Manter a funcionalidade de Contratos.

6.  **[ ] Aba "Franquias":**
    - Criar a interface para administradores (`super_admin`) gerenciarem as unidades.
    - O formulário deve conter todos os novos campos (CNPJ, endereço, etc.) e usar o hook `useCepLookup` para preenchimento automático do endereço.

7.  **[ ] Página "Visão Geral" (Dashboard):**
    - Analisar os componentes do `RelatorioAtendimento.tsx` e `RelatorioFinanceiro.tsx` do projeto convencional.
    - Selecionar os KPIs mais relevantes (ex: Total de Sessões, Total de Faltas, Faturamento no Mês, Ticket Médio) e criar cards de resumo para serem exibidos na página principal (`/dashboard`).

### Fase 3: Testes e Lançamento (1 semana)

1.  **[ ] Testes End-to-End:**
    - Testar todos os fluxos de CRUD (Criar, Ler, Atualizar, Deletar) em todas as seções de Configurações.
    - Validar o controle de acesso, garantindo que usuários com diferentes papéis vejam e possam fazer apenas o que lhes é permitido.
2.  **[ ] Lançamento:**
    - Fazer o deploy do novo código e executar as migrações do banco de dados em ambiente de produção.
