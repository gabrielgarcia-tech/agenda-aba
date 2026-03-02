# Especificação da Interface e Experiência do Usuário (UI/UX)

Este documento descreve as novas telas e componentes de interface para o sistema de agendamento. O design deve ser consistente com a identidade visual existente do NexoABA, utilizando a biblioteca de componentes `shadcn/ui`.

## Novas Páginas

### 1. Página da Agenda (`/agenda`)

Esta será a página central para visualização e gerenciamento de agendamentos. Ela substituirá qualquer funcionalidade de agenda existente.

**Componentes Principais:**

- **Seletor de Visualização:** Botões ou abas para alternar entre "Agenda por Profissional" e "Agenda por Sala".
- **Seletor de Data:** Um mini-calendário para navegar rapidamente para uma data específica.
- **Filtros:** Dropdowns para filtrar por profissional, paciente ou sala (dependendo da visualização).
- **Componente de Calendário:** A área principal, que exibirá os agendamentos. Recomenda-se o uso de uma biblioteca robusta como `FullCalendar` ou `react-big-calendar`.
- **Botão "Novo Agendamento":** Abre um modal para criar um novo agendamento.

**Visualização por Profissional:**

- O calendário será exibido no modo "Resource Timeline", onde cada coluna representa um profissional (`therapist`).
- Os eventos (agendamentos) serão exibidos nas colunas correspondentes aos profissionais associados.

**Visualização por Sala:**

- O calendário será exibido no modo "Resource Timeline", onde cada coluna representa uma sala (`room`).
- Os eventos serão exibidos nas colunas correspondentes às salas onde ocorrem.

### 2. Modal de Criação/Edição de Agendamento

Um formulário completo para criar ou editar agendamentos.

**Campos:**

- **Paciente:** Um campo de busca/seleção para encontrar um paciente.
- **Profissionais:** Um campo de seleção múltipla para associar um ou mais profissionais.
- **Sala:** Um campo de seleção para escolher a sala.
- **Data e Hora de Início/Fim:** Seletores de data e hora.
- **Recorrência:** Um componente para definir regras de recorrência (ex: "Repetir toda semana às segundas, quartas e sextas").
- **Notas:** Um campo de texto para notas adicionais.

## Fluxo do Usuário (Supervisor)

1.  O supervisor navega para a página `/agenda`.
2.  Ele seleciona a visualização desejada (por profissional ou por sala).
3.  Ele clica em um horário vago no calendário ou no botão "Novo Agendamento".
4.  O modal de criação é aberto.
5.  Ele preenche as informações do agendamento, incluindo a recorrência.
6.  Ao salvar, a Edge Function `create-recurring-appointment` é chamada, e o calendário é atualizado para exibir os novos eventos.
7.  Para editar, ele clica em um agendamento existente. O modal de edição é aberto.
8.  Ao salvar as alterações, ele é questionado se deseja aplicar a mudança apenas para aquele evento ou para todos os eventos futuros da série.

## Componentes Reutilizáveis

- **`AppointmentCard`:** Um componente para exibir as informações de um agendamento dentro do calendário.
- **`RecurrenceEditor`:** Um componente para criar e editar regras de recorrência RRULE de forma amigável.


---

## Atualizações da v2 (Baseado na Análise da Planilha)

### 1. Gerenciamento de Salas

- **Página de Gerenciamento de Salas (`/admin/rooms`):**
    - Uma nova página para `admins` e `supervisors` criarem e editarem salas.
    - O formulário de criação/edição de sala deve conter os campos: `name`, `discipline` (dropdown), e `capacity` (input numérico).
    - A interface deve exibir o nome da sala com seus sub-slots (ex: "Sala 1 (A, B, C)" se a capacidade for 3).

### 2. Modal de Agendamento (v2)

- **Tipo de Agendamento:** Adicionar um campo `appointment_type` (dropdown: Clínica, Escolar, Domiciliar, Online).
- **Atendimento em Grupo:**
    - Adicionar um checkbox "Atendimento em Grupo".
    - Se marcado, o campo "Paciente" deve permitir a seleção de múltiplos pacientes.
- **Duração Manual:** Se `allow_manual_duration` for `true` nas configurações da clínica, os campos de `start_time` e `end_time` devem ser editáveis. Caso contrário, o `end_time` é calculado automaticamente com base no `default_session_duration`.

### 3. Visualização do Calendário (v2)

- **Cores:** Os eventos no calendário devem ser coloridos de acordo com as regras da planilha:
    - **Rosa/Magenta:** Para agendamentos com duração diferente da padrão.
    - **Azul Tiffany:** Para atendimentos em grupo.
- **Sub-slots de Sala:** Na visualização por sala, se uma sala tem capacidade > 1, ela deve ser exibida com sub-colunas (ex: Sala 1-A, Sala 1-B) para que os agendamentos simultâneos possam ser visualizados claramente.
