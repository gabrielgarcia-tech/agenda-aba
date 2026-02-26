# Especificação do Banco de Dados - Sistema de Agenda

Este documento detalha as mudanças e adições necessárias ao esquema do banco de dados Supabase para suportar o novo sistema de agendamento. A estrutura foi projetada para ser flexível, escalável e integrada à arquitetura multi-tenant existente do NexoABA.

## Resumo das Mudanças

- **Novas Tabelas:** Serão criadas 4 novas tabelas para gerenciar salas, agendamentos (recorrentes e únicos), e a associação de múltiplos profissionais a um único agendamento.
- **Tabela Depreciada:** A tabela `patient_schedules` será substituída pela nova e mais robusta tabela `appointments`.
- **Configurações:** Uma nova tabela `clinic_settings` será adicionada para gerenciar configurações por franquia, como a duração padrão das sessões.

---

## Novas Tabelas

### 1. `rooms`

Armazena as salas de atendimento de cada clínica.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `clinic_id` | `uuid` | Chave Estrangeira (FK) para `clinics.id` |
| `name` | `text` | Nome da sala (ex: "Sala 1", "Sala Sensorial") |
| `capacity` | `integer` | Capacidade máxima de pessoas na sala (opcional) |
| `description` | `text` | Descrição ou notas sobre a sala (opcional) |
| `created_at` | `timestamptz` | Data/hora de criação |
| `updated_at` | `timestamptz` | Data/hora da última atualização |

### 2. `appointments`

Coração do novo sistema, armazena cada evento de agendamento individual.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `clinic_id` | `uuid` | FK para `clinics.id` |
| `patient_id` | `uuid` | FK para `patients.id` |
| `start_time` | `timestamptz` | Data e hora de início do agendamento |
| `end_time` | `timestamptz` | Data e hora de término do agendamento |
| `room_id` | `uuid` | FK para `rooms.id` (opcional) |
| `status` | `text` | Enum: `scheduled`, `completed`, `cancelled`, `no_show` |
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

### 4. `recurring_appointments`

Define as regras para agendamentos recorrentes.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `clinic_id` | `uuid` | FK para `clinics.id` |
| `patient_id` | `uuid` | FK para `patients.id` |
| `professional_id` | `uuid` | FK para `profiles.id` (profissional principal) |
| `room_id` | `uuid` | FK para `rooms.id` (opcional) |
| `start_time` | `time` | Hora de início (ex: '09:00:00') |
| `end_time` | `time` | Hora de término (ex: '09:50:00') |
| `recurrence_rule` | `text` | Regra no formato iCalendar RRULE (ex: `FREQ=WEEKLY;BYDAY=MO,WE,FR`) |
| `start_date` | `date` | Data de início da recorrência |
| `end_date` | `date` | Data de término da recorrência (opcional) |
| `created_by` | `uuid` | FK para `profiles.id` |
| `created_at` | `timestamptz` | Data/hora de criação |

### 5. `clinic_settings`

Armazena configurações específicas de cada franquia.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `clinic_id` | `uuid` | FK para `clinics.id` (com constraint `UNIQUE`) |
| `default_session_duration` | `integer` | Duração padrão da sessão em minutos (ex: 50) |
| `allow_manual_duration` | `boolean` | Se `true`, permite que a duração seja ajustada manualmente |
| `updated_at` | `timestamptz` | Data/hora da última atualização |

---

## Plano de Migração

1.  **Criar as Novas Tabelas:** Executar um script de migração SQL para criar as tabelas `rooms`, `appointments`, `appointment_professionals`, `recurring_appointments`, e `clinic_settings`.
2.  **Migrar Dados:** Criar um script (preferencialmente uma Edge Function no Supabase) para ler todos os dados da tabela `patient_schedules` e inseri-los na nova tabela `appointments`. A lógica deverá:
    - Para cada registro em `patient_schedules`, criar um registro correspondente em `recurring_appointments` com uma regra semanal (`FREQ=WEEKLY`).
    - Gerar as instâncias individuais em `appointments` para os próximos 12 meses com base na regra de recorrência.
3.  **Depreciar `patient_schedules`:** Após a migração bem-sucedida e validação, a tabela `patient_schedules` pode ser renomeada para `patient_schedules_deprecated` e, eventualmente, removida.
4.  **Atualizar a Aplicação:** O código do frontend (hooks e componentes) deve ser atualizado para usar as novas tabelas e a nova estrutura de dados.
