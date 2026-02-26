# Projeto Agenda ABA

Este repositório contém a documentação técnica e o plano de implementação para um novo e avançado sistema de agendamento para a plataforma NexoABA. O objetivo é criar uma solução de agenda flexível e poderosa que atenda às necessidades complexas de clínicas de Análise do Comportamento Aplicada (ABA), incluindo múltiplas visualizações, gerenciamento por supervisores e configurações personalizadas por franquia.

## Visão Geral

A implementação proposta substituirá e expandirá a funcionalidade de agendamento existente, introduzindo um sistema de calendário completo com duas visualizações principais:

1.  **Agenda por Profissional:** Exibe os compromissos de cada terapeuta.
2.  **Agenda por Sala:** Mostra a ocupação das salas de atendimento da clínica.

Este projeto foi projetado para ser implementado dentro da arquitetura existente do NexoABA, aproveitando seu sistema de autenticação, papéis de usuário e banco de dados Supabase.

## Documentação

A documentação neste repositório está dividida nos seguintes arquivos:

- **[DATABASE.md](./DATABASE.md):** Descreve o novo esquema do banco de dados, incluindo tabelas para salas, agendamentos, e configurações.
- **[API.md](./API.md):** Especifica os novos endpoints de API (ou funções Supabase) necessários para gerenciar a agenda.
- **[UI_UX.md](./UI_UX.md):** Detalha a interface do usuário e a experiência de uso, com wireframes para as novas visualizações de agenda.
- **[PERMISSIONS.md](./PERMISSIONS.md):** Define as regras de controle de acesso para os diferentes papéis de usuário dentro do sistema de agenda.
- **[IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md):** Apresenta um plano de implementação passo a passo para guiar o desenvolvimento.

## Como Usar

Este repositório deve ser usado como a "fonte da verdade" para a implementação do novo sistema de agenda. Desenvolvedores e stakeholders podem consultar estes documentos para entender a arquitetura, o design e os requisitos da funcionalidade.
