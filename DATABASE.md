# Especificação do Banco de Dados - Sistema de Agenda (v2)

Este documento detalha as mudanças e adições necessárias ao esquema do banco de dados Supabase para suportar o novo sistema de agendamento, **incorporando as regras de negócio descobertas na análise da planilha da clínica**.

## Resumo das Mudanças (v2)

- **Tabela `rooms`:** Adicionados campos `discipline` e `capacity` para suportar salas com múltiplos atendimentos simultâneos (sub-slots).
- **Tabela `appointments`:** Adicionados campos `appointment_type` (clínica, escolar, etc.), `is_group_appointment` (para atendimentos duplos), e `group_id`.
- **Tabela `appointment_patients`:** Nova tabela de junção para suportar múltiplos pacientes em um único agendamento (atendimento duplo).
- **Tabela `clinic_settings`:** Adicionado campo `session_break_duration` para o intervalo entre sessões.
- **Tabela `profiles`:** A coluna `role` será alterada para suportar um array de papéis (ex: `["fonoaudiologa", "aplicadora_aba"]`).

---

## Novas Tabelas (v2)

### 1. `rooms`

Armazena as salas de atendimento de cada clínica, com suporte a múltiplos atendimentos simultâneos.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `clinic_id` | `uuid` | Chave Estrangeira (FK) para `clinics.id` |
| `name` | `text` | Nome da sala (ex: "Sala 1", "Sala Sensorial") |
| `discipline` | `text` | Enum: `fonoaudiologia`, `terapia_ocupacional`, `psicologia`, `geral` |
| `capacity` | `integer` | **NOVO:** Número de atendimentos simultâneos (sub-slots) |
| `description` | `text` | Descrição ou notas sobre a sala (opcional) |
| `created_at` | `timestamptz` | Data/hora de criação |
| `updated_at` | `timestamptz` | Data/hora da última atualização |

### 2. `appointments`

Coração do novo sistema, armazena cada evento de agendamento individual.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `clinic_id` | `uuid` | FK para `clinics.id` |
| `start_time` | `timestamptz` | Data e hora de início do agendamento |
| `end_time` | `timestamptz` | Data e hora de término do agendamento |
| `room_id` | `uuid` | FK para `rooms.id` (opcional) |
| `room_slot` | `integer` | **NOVO:** Sub-slot da sala (ex: 1 para Sala 1A, 2 para Sala 1B) |
| `status` | `text` | Enum: `scheduled`, `completed`, `cancelled`, `no_show` |
| `appointment_type` | `text` | **NOVO:** Enum: `clinic`, `school`, `home`, `online` |
| `is_group_appointment` | `boolean` | **NOVO:** `true` se for um atendimento em grupo (duplo ou mais) |
| `group_id` | `uuid` | **NOVO:** ID para agrupar múltiplos `appointments` em um atendimento em grupo |
| `notes` | `text` | Notas sobre o agendamento específico |
| `created_by` | `uuid` | FK para `profiles.id` do usuário que criou |
| `recurring_appointment_id` | `uuid` | FK para `recurring_appointments.id` (se aplicável) |
| `created_at` | `timestamptz` | Data/hora de criação |
| `updated_at` | `timestamptz` | Data/hora da última atualização |

### 3. `appointment_professionals`

Tabela de junção que permite que múltiplos profissionais sejam associados a um único agendamento.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `appointment_id` | `uuid` | PK, FK para `appointments.id` |
| `professional_id` | `uuid` | PK, FK para `profiles.id` |
| `role` | `text` | Papel no agendamento (ex: 'principal', 'assistente') |

### 4. `appointment_patients`

**NOVA TABELA:** Tabela de junção para suportar múltiplos pacientes em um único agendamento.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `appointment_id` | `uuid` | PK, FK para `appointments.id` |
| `patient_id` | `uuid` | PK, FK para `patients.id` |

### 5. `recurring_appointments`

Define as regras para agendamentos recorrentes.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `clinic_id` | `uuid` | FK para `clinics.id` |
| `start_time` | `time` | Hora de início (ex: '09:00:00') |
| `end_time` | `time` | Hora de término (ex: '09:50:00') |
| `recurrence_rule` | `text` | Regra no formato iCalendar RRULE (ex: `FREQ=WEEKLY;BYDAY=MO,WE,FR`) |
| `start_date` | `date` | Data de início da recorrência |
| `end_date` | `date` | Data de término da recorrência (opcional) |
| `created_by` | `uuid` | FK para `profiles.id` |
| `created_at` | `timestamptz` | Data/hora de criação |

### 6. `clinic_settings`

Armazena configurações específicas de cada franquia.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `clinic_id` | `uuid` | FK para `clinics.id` (com constraint `UNIQUE`) |
| `default_session_duration` | `integer` | Duração padrão da sessão em minutos (ex: 50) |
| `session_break_duration` | `integer` | **NOVO:** Duração do intervalo entre sessões em minutos (ex: 10) |
| `allow_manual_duration` | `boolean` | Se `true`, permite que a duração seja ajustada manualmente |
| `updated_at` | `timestamptz` | Data/hora da última atualização |

---

## Plano de Migração (v2)

1.  **Atualizar a Migração:** Modificar o script de migração SQL para incluir os novos campos e a nova tabela `appointment_patients`.
2.  **Atualizar o Script de Migração de Dados:** A Edge Function de migração deve ser atualizada para:
    - Ler os dados da tabela `patient_schedules`.
    - Identificar atendimentos duplos (baseado em notas ou formatação) e criar os registros correspondentes em `appointment_patients`.
    - Criar os registros em `appointments` e `recurring_appointments`.
3.  **Atualizar a Aplicação:** O código do frontend (hooks e componentes) deve ser atualizado para usar a nova estrutura de dados, incluindo o suporte a atendimentos em grupo e tipos de agendamento.
