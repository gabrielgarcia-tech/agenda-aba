# Especificação do Banco de Dados - Módulo de Configurações (v3)

Este documento detalha as mudanças e adições necessárias ao esquema do banco de dados Supabase para suportar o novo **Módulo de Configurações**, espelhando a estrutura do projeto `session-stream-desk` e adaptando-a para a realidade do `agenda-aba`.

## Resumo das Mudanças (v3)

- **Tabela `franchises`:** Será enriquecida com campos de endereço e contato (CNPJ, Razão Social, etc.).
- **Tabela `convenios`:** Nova tabela para armazenar os convênios médicos.
- **Tabela `procedimentos`:** Nova tabela para os procedimentos oferecidos.
- **Tabela `convenio_procedimentos`:** Tabela de junção para vincular procedimentos a convênios com valores específicos.
- **Tabela `recursos_terapeuticos`:** Nova tabela para o cadastro de recursos (materiais, brinquedos, etc.).
- **Tabela `document_categories`:** Nova tabela para categorizar documentos.
- **Tabela `clinic_documents`:** Nova tabela para armazenar documentos da clínica.
- **Tabela `user_roles`:** Será a fonte da verdade para os papéis dos usuários.
- **Tabela `role_permissions`:** Nova tabela para armazenar as permissões de cada papel de forma dinâmica.

---

## Novas Tabelas e Modificações (v3)

### 1. `franchises` (Modificação)

Atualizar a tabela existente `clinics` (ou `franchises` se já renomeada) para incluir informações detalhadas de cada unidade.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `name` | `text` | Nome da unidade (ex: "Piracicaba") |
| `cnpj` | `text` | **NOVO:** CNPJ da unidade |
| `razao_social` | `text` | **NOVO:** Razão Social da unidade |
| `email` | `text` | **NOVO:** E-mail de contato da unidade |
| `telefone` | `text` | **NOVO:** Telefone de contato da unidade |
| `cep` | `text` | **NOVO:** CEP do endereço |
| `estado` | `text` | **NOVO:** Estado (UF) |
| `cidade` | `text` | **NOVO:** Cidade |
| `rua` | `text` | **NOVO:** Rua / Logradouro |
| `numero` | `text` | **NOVO:** Número do endereço |
| `bairro` | `text` | **NOVO:** Bairro |

### 2. `convenios` (Nova)

Armazena os convênios aceitos pela clínica.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `franchise_id` | `uuid` | FK para `franchises.id` |
| `nome` | `text` | Nome do convênio (ex: "Unimed") |
| `cnpj` | `text` | CNPJ do convênio (opcional) |
| `ativo` | `boolean` | `true` se o convênio está ativo |

### 3. `procedimentos` (Nova)

Armazena os procedimentos oferecidos.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `franchise_id` | `uuid` | FK para `franchises.id` |
| `nome` | `text` | Nome do procedimento (ex: "Sessão de Fonoaudiologia") |
| `codigo` | `text` | Código do procedimento (opcional) |
| `descricao` | `text` | Descrição detalhada (opcional) |

### 4. `convenio_procedimentos` (Nova)

Tabela de junção para definir os valores de cada procedimento por convênio.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `convenio_id` | `uuid` | PK, FK para `convenios.id` |
| `procedimento_id` | `uuid` | PK, FK para `procedimentos.id` |
| `valor` | `numeric` | Valor do procedimento para este convênio específico |

### 5. `recursos_terapeuticos` (Nova)

Cadastro de recursos terapêuticos.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `franchise_id` | `uuid` | FK para `franchises.id` |
| `nome` | `text` | Nome do recurso (ex: "Bola de Pilates") |
| `descricao` | `text` | Descrição e observações |
| `file_path` | `text` | Caminho para foto ou anexo no Supabase Storage |
| `file_name` | `text` | Nome do arquivo da foto/anexo |

### 6. `role_permissions` (Nova)

Armazena as permissões para cada papel, permitindo edição dinâmica.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `role` | `text` | PK, Nome do papel (ex: `terapeuta`, `recepcao`) |
| `permissions` | `text[]` | PK, Array de strings de permissão (ex: `["patient:read", "appointment:create"]`) |

### 7. `document_categories` e `clinic_documents` (Novas)

Para gerenciamento de documentos, sem a parte de anamnese.

**`document_categories`**
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | PK |
| `franchise_id` | `uuid` | FK para `franchises.id` |
| `name` | `text` | Nome da categoria (ex: "Contratos", "Documentos Internos") |

**`clinic_documents`**
| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | PK |
| `franchise_id` | `uuid` | FK para `franchises.id` |
| `category_id` | `uuid` | FK para `document_categories.id` |
| `name` | `text` | Nome do documento |
| `file_path` | `text` | Caminho para o arquivo no Supabase Storage |
| `file_name` | `text` | Nome do arquivo |
