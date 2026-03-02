# Plano de Implementação

Este documento descreve um plano passo a passo para a implementação do novo sistema de agendamento.

## Fases

### Fase 1: Backend e Banco de Dados (1-2 semanas)

1.  **[ ] Migração do Banco de Dados:**
    - Criar um novo arquivo de migração SQL no diretório `supabase/migrations`.
    - Adicionar o SQL para criar as tabelas: `rooms`, `appointments`, `appointment_professionals`, `recurring_appointments`, e `clinic_settings`.
    - Adicionar as políticas de RLS para todas as novas tabelas.
2.  **[ ] Edge Functions:**
    - Desenvolver e testar as Edge Functions: `create-recurring-appointment`, `update-appointment`, e `get-calendar-events`.
3.  **[ ] Script de Migração de Dados:**
    - Criar uma Edge Function temporária para migrar os dados da tabela `patient_schedules` para a nova estrutura.
    - Executar o script em ambiente de desenvolvimento e validar os dados.

### Fase 2: Frontend (2-3 semanas)

1.  **[ ] Hooks de Dados:**
    - Criar novos hooks React Query (`useAppointments`, `useRooms`, etc.) para interagir com as novas Edge Functions.
2.  **[ ] Componentes da UI:**
    - Desenvolver os componentes reutilizáveis `AppointmentCard` e `RecurrenceEditor`.
3.  **[ ] Página da Agenda:**
    - Criar a nova página `/agenda`.
    - Integrar uma biblioteca de calendário (ex: `FullCalendar`).
    - Configurar as visualizações "por profissional" e "por sala".
    - Conectar os filtros e o seletor de data.
4.  **[ ] Modal de Agendamento:**
    - Desenvolver o modal de criação/edição de agendamento.
    - Integrar o formulário com o hook para criar/atualizar agendamentos.

### Fase 3: Testes e Lançamento (1 semana)

1.  **[ ] Testes End-to-End:**
    - Testar o fluxo completo de criação, edição e exclusão de agendamentos recorrentes e únicos.
    - Validar as permissões para todos os papéis de usuário.
2.  **[ ] Lançamento (Staging):**
    - Fazer o deploy do novo código em um ambiente de staging.
    - Executar o script de migração de dados no banco de dados de staging.
    - Realizar testes de aceitação com os stakeholders.
3.  **[ ] Lançamento (Produção):**
    - Agendar uma janela de manutenção.
    - Fazer o deploy do código em produção.
    - Executar o script de migração de dados no banco de dados de produção.
    - Monitorar por erros e feedback do usuário.


---

## Checklist de Tarefas Adicionais (v2)

### Backend

- **[ ] Modificar `create-recurring-appointment`:**
    - Adicionar suporte para `appointment_type`.
    - Adicionar lógica para criar registros em `appointment_patients` se for um atendimento em grupo.
- **[ ] Modificar `get-calendar-events`:**
    - Juntar informações de `appointment_patients`.
    - Retornar `is_group_appointment` e `appointment_type` para o frontend.

### Frontend

- **[ ] Criar Página de Gerenciamento de Salas (`/admin/rooms`):**
    - Formulário para criar/editar salas com `name`, `discipline`, e `capacity`.
- **[ ] Atualizar Modal de Agendamento:**
    - Adicionar campo `appointment_type`.
    - Adicionar checkbox "Atendimento em Grupo" e campo de seleção múltipla de pacientes.
- **[ ] Atualizar Visualização do Calendário:**
    - Implementar a lógica de cores para horários divergentes e atendimentos em grupo.
    - Implementar a visualização de sub-slots para salas com capacidade > 1.
