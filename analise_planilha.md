# Análise da Planilha de Agenda da Clínica

## Estrutura Geral

- A planilha possui uma aba de resumo ("Atendimentos") e uma aba por profissional.
- Cada aba de profissional tem: coluna de Horários + colunas por dia da semana (Segunda a Sexta).
- Os horários são blocos fixos de 50 minutos (ex: 08h00-08h50, 08h50-09h40, 09h50-10h40, 10h40-11h30...).
- Existe um intervalo de 10 minutos entre os blocos (ex: 08h50 → 09h50 = 60 min, mas o bloco é de 50 min).
- Os blocos de tarde começam às 13h40.

## Profissionais Identificados

### Fonoaudiologia (FONO)
- Leonice Borges
- Elen Prado
- Thais Hernandes
- Leticia Ribeiro (Fono / Aplicadora ABA) ← profissional com dupla função

### Terapia Ocupacional (TO)
- Rosana Turcato
- Marcela Borilli
- Larissa Thais

### Psicologia / ABA (PSICO)
- Lucas Miguel
- Isabella Cunha (Psicóloga / Aplicadora ABA)
- Brenda Lopes (Aplicadora ABA)
- Camila Stoco (Coordenadora ABA)
- Leticia Rossi (Psicóloga / Especialista ABA)
- Victor Fontolan (Psicólogo / Aplicador ABA)
- Juliana Santos (Aplicadora ABA)
- Théo Oliveira (Psicólogo / Aplicadora ABA)
- Rosilene Ferreira (Aplicadora ABA)
- Isadora Fonseca (Aplicadora ABA)
- Giovana Marques (Aplicadora ABA)
- Leticia Ribeiro (Aplicadora ABA)

## Legenda de Cores (Regras de Negócio)

| Cor | Significado |
|-----|-------------|
| Amarelo | Horário VAGO (sem paciente agendado) |
| Rosa/Magenta | Horário DIVERGENTE (fora do padrão de horário da franquia) |
| Azul Tiffany (ciano) | ATENDIMENTO DUPLO (1 profissional → 2 pacientes simultâneos) |
| Sem cor (branco) | Atendimento normal |

## Observações Importantes (Conflitos com a Implementação)

1. **Atendimento Duplo (Azul Tiffany):** Um profissional atende 2 pacientes ao mesmo tempo. Na planilha, isso aparece como uma célula com cor azul tiffany contendo o nome de ambos os pacientes ou uma nota especial. Na implementação atual, a tabela `appointment_professionals` prevê múltiplos profissionais por agendamento, mas não o inverso (múltiplos pacientes por profissional). Isso precisa ser adicionado.

2. **Horários Divergentes (Rosa):** Alguns atendimentos têm horários que fogem do padrão de 50 minutos. Ex: "Das 09h40 às 10h30 - Theodoro de Andrade Camargo" (na agenda de Leonice) ou "Das 15h20 às 16h10 Vitoria Barbosa Fagundes" (na agenda de Brenda). Isso confirma a necessidade do campo `allow_manual_duration` na tabela `clinic_settings` e de um campo de duração customizada por agendamento.

3. **Atendimento Escolar:** Na agenda de Brenda, existem entradas como "Atendimento Escolar: Thomas Massaki Katumata Cardoso". Isso é um tipo especial de atendimento que ocorre fora da clínica. O sistema precisa suportar um campo `appointment_type` (ex: `clinic`, `school`, `home`).

4. **Saída Antecipada:** Existe uma entrada "Saída 17h30" na agenda de Brenda. Isso não é um atendimento, mas uma nota de disponibilidade do profissional. O sistema precisa suportar bloqueios de horário/indisponibilidade.

5. **Profissionais com Dupla Função:** Leticia Ribeiro é tanto Fonoaudióloga quanto Aplicadora ABA. O sistema de papéis precisa suportar múltiplas especialidades por profissional.

6. **Duração Padrão de Sessão:** Os blocos são de 50 minutos, com 10 minutos de intervalo. A `clinic_settings` deve ter `default_session_duration = 50` e `session_break_duration = 10`.

7. **Salas Não Presentes:** A planilha não contém informação de sala. Isso confirma que as salas precisam ser cadastradas manualmente no sistema.

8. **Estrutura de Salas com Sub-slots (A, B, C):** O usuário descreveu que salas podem ter múltiplos atendimentos simultâneos, identificados por letras (Sala 1A, 1B, 1C). Isso precisa ser modelado na tabela `rooms` com um campo `capacity` (número de atendimentos simultâneos) e a geração automática dos sub-slots.
