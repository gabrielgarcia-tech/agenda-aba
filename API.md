# Especificação da API (Supabase Edge Functions)

Este documento descreve as novas Edge Functions necessárias para suportar a lógica de negócios do sistema de agendamento. Essas funções encapsularão operações complexas, garantindo a integridade dos dados e a segurança.

## Funções

### 1. `create-recurring-appointment`

Cria um agendamento recorrente e gera as instâncias individuais.

- **Método:** `POST`
- **Parâmetros:**
    - `patient_id`
    - `professional_id`
    - `room_id` (opcional)
    - `start_time`
    - `end_time`
    - `recurrence_rule` (formato RRULE)
    - `start_date`
    - `end_date` (opcional)
- **Lógica:**
    1.  Valida as permissões do usuário (supervisor ou admin).
    2.  Cria um novo registro na tabela `recurring_appointments`.
    3.  Usa uma biblioteca como `rrule.js` para calcular todas as ocorrências entre `start_date` e `end_date` (ou um período padrão, ex: 1 ano).
    4.  Para cada ocorrência, insere um novo registro na tabela `appointments`.
    5.  Retorna sucesso ou erro.

### 2. `update-appointment`

Atualiza um agendamento, lidando com casos de recorrência.

- **Método:** `POST`
- **Parâmetros:**
    - `appointment_id`
    - `start_time` (opcional)
    - `end_time` (opcional)
    - `room_id` (opcional)
    - `professional_ids` (array de UUIDs, opcional)
    - `update_scope` (Enum: `this_event`, `this_and_future_events`)
- **Lógica:**
    1.  Valida as permissões.
    2.  Se `update_scope` for `this_event`:
        - Atualiza apenas o registro `appointments` especificado.
    3.  Se `update_scope` for `this_and_future_events`:
        - Modifica o `recurring_appointments` original, definindo um `end_date` para o dia do evento atualizado.
        - Cria um novo `recurring_appointments` com as novas informações a partir da data do evento.
        - Exclui e recria os futuros `appointments` individuais.
    4.  Retorna sucesso ou erro.

### 3. `get-calendar-events`

Busca os agendamentos para um determinado período e visualização.

- **Método:** `GET`
- **Parâmetros:**
    - `start_date` (ISO string)
    - `end_date` (ISO string)
    - `view_type` (Enum: `professional`, `room`)
    - `clinic_id`
- **Lógica:**
    1.  Busca todos os `appointments` dentro do intervalo de datas para a `clinic_id`.
    2.  Junta as informações de `patients`, `rooms`, e `appointment_professionals`.
    3.  Formata os dados na estrutura esperada por uma biblioteca de calendário como `FullCalendar`.
    4.  Se `view_type` for `professional`, agrupa os eventos por profissional.
    5.  Se `view_type` for `room`, agrupa os eventos por sala.
    6.  Retorna um array de eventos formatados.
