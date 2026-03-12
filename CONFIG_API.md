# Especificação da API (Supabase Edge Functions) - Módulo de Configurações (v3)

Este documento descreve as novas Edge Functions necessárias para suportar a lógica de negócios do Módulo de Configurações.

## Funções

### 1. `admin-manage-staff`

Gerencia a equipe (funcionários não-terapeutas), incluindo convites e atribuição de papéis.

- **Método:** `POST`
- **Parâmetros:**
    - `action`: `'list' | 'invite' | 'update' | 'delete'`
    - `franchise_id`: `string`
    - `user_id?`: `string` (para `update`, `delete`)
    - `email?`: `string` (para `invite`)
    - `role?`: `AppRole` (para `invite`, `update`)
- **Lógica:**
    - **`list`**: Retorna todos os usuários (`profiles`) vinculados à `franchise_id` que não são terapeutas.
    - **`invite`**: Usa a API Admin do Supabase para convidar um novo usuário por e-mail e o associa à `franchise_id` e ao `role` especificado.
    - **`update`**: Atualiza o `role` de um `user_id` existente na tabela `user_roles`.
    - **`delete`**: Remove o vínculo do usuário com a clínica (não apaga o usuário do Supabase Auth).

### 2. `get-role-permissions`

Busca as permissões de um ou todos os papéis.

- **Método:** `GET`
- **Parâmetros:**
    - `role?`: `string` (opcional, se não fornecido, retorna todos)
- **Lógica:**
    1. Busca os dados na tabela `role_permissions`.
    2. Se um `role` específico for solicitado, retorna apenas suas permissões.
    3. Caso contrário, retorna um objeto mapeando cada papel ao seu array de permissões.

### 3. `update-role-permissions`

Atualiza as permissões de um papel específico.

- **Método:** `POST`
- **Parâmetros:**
    - `role`: `string`
    - `permissions`: `string[]` (array completo de permissões para aquele papel)
- **Lógica:**
    1. Valida que o usuário tem a permissão `config:access`.
    2. Executa um `UPSERT` na tabela `role_permissions`, substituindo o array de permissões do papel especificado.
    3. Retorna sucesso ou erro.

### 4. `admin-manage-franchises`

Cria, atualiza e gerencia as informações das franquias/unidades.

- **Método:** `POST`
- **Parâmetros:**
    - `action`: `'create' | 'update'`
    - `franchise_id?`: `string` (para `update`)
    - `data`: Objeto com os campos da tabela `franchises` (CNPJ, endereço, etc.).
- **Lógica:**
    1. Valida que o usuário é `super_admin`.
    2. Executa a operação de `INSERT` ou `UPDATE` na tabela `franchises`.
    3. Retorna a franquia criada/atualizada.
