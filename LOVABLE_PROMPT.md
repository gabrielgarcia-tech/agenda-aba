# Prompt Completo para Implementação no Lovable

> Copie e cole o conteúdo abaixo diretamente no chat do Lovable.

---

Preciso que você implemente um sistema completo de agenda no projeto NexoABA. Leia com atenção todas as instruções abaixo antes de escrever qualquer código.

---

## CONTEXTO DO PROJETO ATUAL

O projeto já possui as seguintes estruturas que você deve preservar e integrar:

- **Tabela `patient_schedules`** (migração `20260226192839`): tabela existente com agendamentos básicos. Ela é a base de partida, mas será substituída pela nova arquitetura descrita abaixo.
- **Hook `usePatientSchedules`**: já existe em `src/hooks/usePatientSchedules.tsx`.
- **Tabelas existentes no Supabase:** `patients`, `therapists`, `clinics`, `profiles`, `sessions`.
- **Papéis de usuário existentes:** `supervisor`, `admin`, `therapist`, `super_admin`.
- **Hook `useUserRole`**: já existe no projeto e deve ser usado para controle de acesso no frontend.
- **Stack:** React + TypeScript + Vite + TailwindCSS + shadcn/ui + React Query + React Router v6 + Supabase.

---

## REGRAS DE NEGÓCIO CRÍTICAS (descobertas na planilha real da clínica)

Estas regras são fundamentais e devem guiar toda a implementação:

**1. Duração padrão de sessão:** Cada sessão dura **50 minutos**, com **10 minutos de intervalo** entre sessões. Os blocos de horário seguem o padrão: 08h00–08h50, 08h50–09h40, 09h50–10h40, 10h40–11h30 (manhã) e 13h40–14h30, 14h30–15h20, 15h30–16h20, 16h20–17h10, 17h20–18h10, 18h10–19h00, 19h00–19h50 (tarde).

**2. Atendimento Duplo (Grupo):** Um profissional pode atender 2 ou mais pacientes simultaneamente. No calendário, esse tipo de evento deve ser exibido em **azul tiffany** (`#81D8D0`). Isso exige uma tabela de junção separada (`appointment_patients`) para associar múltiplos pacientes a um único agendamento.

**3. Horários Divergentes:** Alguns atendimentos têm duração diferente do padrão de 50 minutos (ex: "Das 09h40 às 10h30"). No calendário, esses eventos devem ser exibidos em **rosa/magenta** (`#FF69B4`). Isso exige o campo `allow_manual_duration` nas configurações da clínica.

**4. Tipos de Atendimento:** Existem sessões realizadas fora da clínica. O sistema deve suportar os tipos: `clinic` (padrão), `school` (atendimento escolar), `home` (domiciliar) e `online`.

**5. Salas com Sub-slots:** Uma sala pode comportar múltiplos atendimentos simultâneos. Uma sala com `capacity = 3` gera os sub-slots A, B e C (ex: "Sala 1-A", "Sala 1-B", "Sala 1-C"). Na visualização por sala, cada sub-slot deve ser exibido como uma sub-coluna separada.

**6. Profissionais com Dupla Função:** Um profissional pode ter mais de uma especialidade (ex: Fonoaudióloga + Aplicadora ABA). O sistema de filtros deve considerar isso.

---

## BANCO DE DADOS — MIGRAÇÕES SQL

Crie um novo arquivo de migração em `supabase/migrations/` com o seguinte SQL:

### Tabela `rooms`
```sql
CREATE TABLE rooms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  discipline TEXT CHECK (discipline IN ('fonoaudiologia', 'terapia_ocupacional', 'psicologia', 'geral')) DEFAULT 'geral',
  capacity INTEGER NOT NULL DEFAULT 1,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE rooms ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Clinic members can view rooms" ON rooms FOR SELECT USING (clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid()));
CREATE POLICY "Admins and supervisors can manage rooms" ON rooms FOR ALL USING (clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'supervisor', 'super_admin')));
```

### Tabela `appointments`
```sql
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL,
  room_id UUID REFERENCES rooms(id) ON DELETE SET NULL,
  room_slot INTEGER DEFAULT 1,
  status TEXT CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')) DEFAULT 'scheduled',
  appointment_type TEXT CHECK (appointment_type IN ('clinic', 'school', 'home', 'online')) DEFAULT 'clinic',
  is_group_appointment BOOLEAN DEFAULT FALSE,
  group_id UUID,
  notes TEXT,
  created_by UUID REFERENCES profiles(id),
  recurring_appointment_id UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Clinic members can view appointments" ON appointments FOR SELECT USING (clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid()));
CREATE POLICY "Admins and supervisors can manage appointments" ON appointments FOR ALL USING (clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'supervisor', 'super_admin')));
```

### Tabela `appointment_professionals`
```sql
CREATE TABLE appointment_professionals (
  appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
  professional_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  role TEXT DEFAULT 'principal',
  PRIMARY KEY (appointment_id, professional_id)
);
ALTER TABLE appointment_professionals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Clinic members can view appointment_professionals" ON appointment_professionals FOR SELECT USING (appointment_id IN (SELECT id FROM appointments WHERE clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid())));
CREATE POLICY "Admins and supervisors can manage appointment_professionals" ON appointment_professionals FOR ALL USING (appointment_id IN (SELECT id FROM appointments WHERE clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'supervisor', 'super_admin'))));
```

### Tabela `appointment_patients`
```sql
CREATE TABLE appointment_patients (
  appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
  patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  PRIMARY KEY (appointment_id, patient_id)
);
ALTER TABLE appointment_patients ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Clinic members can view appointment_patients" ON appointment_patients FOR SELECT USING (appointment_id IN (SELECT id FROM appointments WHERE clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid())));
CREATE POLICY "Admins and supervisors can manage appointment_patients" ON appointment_patients FOR ALL USING (appointment_id IN (SELECT id FROM appointments WHERE clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'supervisor', 'super_admin'))));
```

### Tabela `recurring_appointments`
```sql
CREATE TABLE recurring_appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  recurrence_rule TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE,
  created_by UUID REFERENCES profiles(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE recurring_appointments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Clinic members can view recurring_appointments" ON recurring_appointments FOR SELECT USING (clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid()));
CREATE POLICY "Admins and supervisors can manage recurring_appointments" ON recurring_appointments FOR ALL USING (clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'supervisor', 'super_admin')));
```

### Tabela `clinic_settings`
```sql
CREATE TABLE clinic_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL UNIQUE REFERENCES clinics(id) ON DELETE CASCADE,
  default_session_duration INTEGER DEFAULT 50,
  session_break_duration INTEGER DEFAULT 10,
  allow_manual_duration BOOLEAN DEFAULT TRUE,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE clinic_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Clinic members can view clinic_settings" ON clinic_settings FOR SELECT USING (clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid()));
CREATE POLICY "Admins and supervisors can manage clinic_settings" ON clinic_settings FOR ALL USING (clinic_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid() AND role IN ('admin', 'supervisor', 'super_admin')));
```

---

## EDGE FUNCTIONS (Supabase)

Crie as seguintes Edge Functions em `supabase/functions/`:

### `create-recurring-appointment` (POST)
Recebe: `{ patient_ids: string[], professional_ids: string[], room_id?: string, room_slot?: number, start_time: string, end_time: string, recurrence_rule: string, start_date: string, end_date?: string, appointment_type: string, is_group_appointment: boolean, notes?: string }`.
Lógica: (1) Valida que o usuário é `admin` ou `supervisor`. (2) Cria o registro em `recurring_appointments`. (3) Usa `rrule` para calcular todas as ocorrências. (4) Para cada ocorrência, insere em `appointments`. (5) Para cada agendamento, insere em `appointment_professionals` e `appointment_patients`. (6) Retorna `{ success: true, count: number }`.

### `update-appointment` (POST)
Recebe: `{ appointment_id: string, start_time?: string, end_time?: string, room_id?: string, professional_ids?: string[], patient_ids?: string[], update_scope: 'this_event' | 'this_and_future_events' }`.
Lógica: (1) Valida permissões. (2) Se `this_event`, atualiza apenas o registro especificado. (3) Se `this_and_future_events`, encerra a recorrência original na data do evento e cria uma nova série a partir daí. (4) Retorna `{ success: true }`.

### `get-calendar-events` (GET)
Recebe: `?start_date=&end_date=&view_type=professional|room&clinic_id=`.
Lógica: (1) Busca todos os `appointments` no período para a clínica. (2) Faz JOIN com `appointment_patients`, `appointment_professionals`, `rooms`, `patients`, `profiles`. (3) Formata para o padrão do FullCalendar: `{ id, title, start, end, resourceId, extendedProps: { appointment_type, is_group_appointment, status, patients, professionals, room } }`. (4) Para eventos em grupo (`is_group_appointment = true`), define `backgroundColor: '#81D8D0'`. (5) Para eventos com duração diferente do padrão, define `backgroundColor: '#FF69B4'`. (6) Retorna o array de eventos.

---

## FRONTEND — HOOKS

Crie os seguintes hooks em `src/hooks/`:

- **`useAppointments.tsx`**: usa React Query para chamar `get-calendar-events`. Aceita parâmetros `startDate`, `endDate`, `viewType`.
- **`useRooms.tsx`**: busca todas as salas da clínica do usuário via Supabase client direto.
- **`useClinicSettings.tsx`**: busca as configurações da clínica do usuário.
- **`useCreateAppointment.tsx`**: mutation que chama `create-recurring-appointment`.
- **`useUpdateAppointment.tsx`**: mutation que chama `update-appointment`.

---

## FRONTEND — PÁGINAS E COMPONENTES

### 1. Página da Agenda (`src/pages/Agenda.tsx`)

Adicione a rota `/agenda` protegida por `ProtectedRoute` no `App.tsx` e o item "Agenda" no menu lateral (`Sidebar`).

A página deve conter:
- **Seletor de visualização** (botões): "Por Profissional" e "Por Sala".
- **Seletor de semana**: navegação para semana anterior/próxima.
- **Filtros**: dropdown de profissional (na visualização por profissional) e dropdown de sala (na visualização por sala).
- **Botão "Novo Agendamento"**: visível apenas para `admin` e `supervisor` (usar `useUserRole`).
- **Componente de calendário** usando `FullCalendar` com a view `resourceTimeGridWeek`. Cada recurso é um profissional ou uma sala. Para salas com `capacity > 1`, gerar sub-recursos (ex: "Sala 1-A", "Sala 1-B").
- **Clique em evento**: abre o modal de edição.
- **Clique em horário vago**: abre o modal de criação (apenas para `admin` e `supervisor`).

### 2. Modal de Agendamento (`src/components/agenda/AppointmentModal.tsx`)

Um `Dialog` do shadcn/ui com os seguintes campos:

| Campo | Tipo | Regra |
| :--- | :--- | :--- |
| Tipo de Atendimento | `Select` | Opções: Clínica, Escolar, Domiciliar, Online |
| Atendimento em Grupo | `Checkbox` | Quando marcado, o campo de paciente vira multi-select |
| Paciente(s) | `Combobox` (single ou multi) | Busca na tabela `patients` |
| Profissional(is) | `Combobox` multi-select | Busca na tabela `profiles` com role `therapist` |
| Sala | `Select` | Busca na tabela `rooms` |
| Sub-slot da Sala | `Select` | Aparece apenas se a sala tiver `capacity > 1` (opções: A, B, C...) |
| Data | `DatePicker` | — |
| Horário de Início | `TimePicker` | — |
| Horário de Término | `TimePicker` | Calculado automaticamente (início + `default_session_duration`). Editável se `allow_manual_duration = true` |
| Recorrência | `RecurrenceEditor` | Componente customizado para selecionar dias da semana e período |
| Notas | `Textarea` | Opcional |

Ao salvar, chamar `useCreateAppointment` ou `useUpdateAppointment`. Se for edição de evento recorrente, exibir um `AlertDialog` perguntando: "Alterar apenas este evento ou este e todos os futuros?".

### 3. Página de Gerenciamento de Salas (`src/pages/admin/Rooms.tsx`)

Acessível apenas para `admin` e `supervisor`. Adicionar rota `/admin/rooms`.

A página deve exibir uma tabela com as salas cadastradas e um botão "Nova Sala". O formulário de criação/edição deve conter: `name` (input), `discipline` (select), `capacity` (input numérico, mínimo 1), `description` (textarea). Exibir o nome da sala com seus sub-slots (ex: "Sala 1 (A, B, C)" se `capacity = 3`).

---

## PERMISSÕES (resumo)

| Papel | Criar/Editar/Excluir Agendamentos | Gerenciar Salas | Visualizar Agenda |
| :--- | :--- | :--- | :--- |
| `super_admin` / `admin` / `supervisor` | Sim | Sim | Sim |
| `therapist` | Não | Não | Sim (agenda geral + própria) |

No frontend, use o hook `useUserRole` para renderizar condicionalmente os botões de ação. No backend (Edge Functions), valide o papel antes de qualquer operação de escrita.

---

## ORDEM DE IMPLEMENTAÇÃO SUGERIDA

1. Criar a migração SQL com todas as tabelas.
2. Criar as Edge Functions `create-recurring-appointment`, `update-appointment` e `get-calendar-events`.
3. Criar os hooks `useRooms`, `useClinicSettings`, `useAppointments`, `useCreateAppointment`, `useUpdateAppointment`.
4. Criar o componente `RecurrenceEditor`.
5. Criar o `AppointmentModal`.
6. Criar a página `/agenda` com o FullCalendar integrado.
7. Criar a página `/admin/rooms`.
8. Adicionar as rotas e os itens de menu.
9. Instalar dependências necessárias: `@fullcalendar/react`, `@fullcalendar/resource-timegrid`, `@fullcalendar/interaction`, `rrule`.
