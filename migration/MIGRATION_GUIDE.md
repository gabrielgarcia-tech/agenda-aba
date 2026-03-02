# Guia de Migração de Agendamentos

Este guia descreve o processo de 3 passos para migrar os agendamentos da planilha para a plataforma NexoABA de forma segura e eficiente.

## Passo 1: Preencher o Arquivo CSV

O arquivo `appointments_template.csv` é o modelo que você deve usar. Ele contém as colunas necessárias para a importação.

**Instruções:**

1.  **Abra o `appointments_template.csv`** em um editor de planilhas (Google Sheets, Excel, etc.).
2.  **Copie e cole os dados da sua planilha de agenda** para as colunas correspondentes.
3.  **Siga o formato exato** para cada coluna:

| Coluna | Formato | Exemplo | Obrigatório |
| :--- | :--- | :--- | :--- |
| `start_time` | `YYYY-MM-DD HH:MM:SS` | `2026-03-02 08:00:00` | Sim |
| `end_time` | `YYYY-MM-DD HH:MM:SS` | `2026-03-02 08:50:00` | Sim |
| `professional_full_name` | Nome completo (idêntico ao da plataforma) | `Leonice Borges` | Sim |
| `patient_full_name` | Nome completo (idêntico ao da plataforma) | `Gabriel Rodrigues Jacinto` | Sim |
| `appointment_type` | `clinic`, `school`, `home`, `online` | `school` | Sim |
| `is_group_appointment` | `true` ou `false` | `true` | Sim |
| `notes` | Texto livre | `Atendimento em grupo` | Não |

**Atenção:**

-   Para atendimentos em grupo, crie uma linha para cada paciente no mesmo horário, com `is_group_appointment` como `true`.
-   Garanta que os nomes dos profissionais e pacientes no CSV são **exatamente** os mesmos que estão cadastrados na plataforma.

4.  **Salve o arquivo preenchido** com o nome `appointments.csv` na raiz do projeto.

## Passo 2: Executar o Script SQL

O script `2_import_appointments.sql` fará a importação dos dados do arquivo `appointments.csv` para o banco de dados da plataforma.

**Instruções para o Lovable ou Desenvolvedor:**

1.  **Acesse o editor SQL do Supabase** no painel do projeto.
2.  **Crie uma nova query**.
3.  **Copie e cole o conteúdo completo** do arquivo `2_import_appointments.sql` no editor.
4.  **Execute a query**.

O script irá:

-   Criar uma tabela temporária `temp_appointments`.
-   Copiar os dados do `appointments.csv` para a tabela temporária.
-   Inserir os dados nas tabelas `appointments`, `appointment_patients` e `appointment_professionals`, buscando os IDs corretos de pacientes e profissionais a partir dos nomes.
-   Deletar a tabela temporária.

## Passo 3: Verificar os Dados

Após a execução do script, acesse a página `/agenda` na plataforma e verifique se os agendamentos foram importados corretamente.
