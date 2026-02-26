# Especificação de Permissões (Controle de Acesso)

Este documento define as permissões para os diferentes papéis de usuário no novo sistema de agendamento, garantindo que apenas usuários autorizados possam realizar ações sensíveis.

## Papéis e Ações

| Papel | Ação | Permissão |
| :--- | :--- | :--- |
| `supervisor` / `admin` | Criar/Editar/Excluir Agendamentos | **Permitido** |
| `supervisor` / `admin` | Criar/Editar/Excluir Salas | **Permitido** |
| `supervisor` / `admin` | Acessar a página de configurações da agenda | **Permitido** |
| `therapist` | Visualizar a agenda completa (por sala) | **Permitido** |
| `therapist` | Visualizar sua própria agenda (por profissional) | **Permitido** |
| `therapist` | Criar/Editar/Excluir Agendamentos | **Negado** |
| `patient` / `guardian` | Visualizar a agenda do paciente | A ser definido (escopo futuro) |

## Implementação Técnica

- **Políticas de RLS (Row-Level Security) no Supabase:** As políticas de segurança nas tabelas `appointments`, `rooms`, etc., garantirão que um usuário só possa ver ou modificar dados pertencentes à sua clínica (`clinic_id`).
- **Verificação de Papel no Frontend:** O frontend usará o hook `useUserRole` para renderizar condicionalmente os botões de edição e exclusão. Por exemplo, o botão "Novo Agendamento" só será visível para `supervisor` e `admin`.
- **Verificação de Papel no Backend:** As Edge Functions verificarão o papel do usuário que está fazendo a chamada antes de executar qualquer operação de escrita (criação, atualização, exclusão).
