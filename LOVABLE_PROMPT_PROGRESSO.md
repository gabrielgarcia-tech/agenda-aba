# Prompt Completo para Implementação do Módulo de Progresso Qualitativo com IA

> Copie e cole o conteúdo abaixo diretamente no chat do Lovable.

---

**AVISO IMPORTANTE: Preserve todo o código e estrutura de arquivos existentes. Não remova, não reescreva e não substitua nenhum arquivo ou rota já criada. Apenas adicione as novas funcionalidades conforme descrito abaixo, integrando-as ao projeto `agenda-aba` existente.**

Preciso que você implemente um novo sistema de registro de progresso do paciente e geração de relatórios com IA. O objetivo é capturar dados quantitativos e qualitativos durante as sessões para que um agente de IA possa gerar relatórios de evolução completos e automáticos.

Leia com atenção todas as instruções e siga a ordem exata das fases. Para cada fase, consulte os arquivos de planejamento correspondentes no repositório (`PROGRESSO_DATABASE.md`, `PROGRESSO_API.md`, `PROGRESSO_IMPLEMENTATION_PLAN.md`).

---

## FASE 1: BACKEND E CAPTURA DE DADOS

### 1.1. Banco de Dados

Crie um novo arquivo de migração em `supabase/migrations/` e adicione o SQL para criar as tabelas `session_entries` e `session_skill_ratings`, conforme especificado no arquivo `PROGRESSO_DATABASE.md`.

### 1.2. Edge Functions (API)

Crie as Edge Functions `transcribe-audio-note` e `save-session-entry` no diretório `supabase/functions/`, conforme especificado no arquivo `PROGRESSO_API.md`.

### 1.3. Interface de Finalização de Sessão

Crie uma nova página/modal que será exibida quando o terapeuta finalizar uma sessão na agenda. Esta interface deve conter os seguintes componentes, na ordem:

1.  **Habilidades Trabalhadas (Quantitativo):**
    - Uma lista das habilidades do checklist do paciente.
    - Para cada habilidade trabalhada na sessão, o terapeuta deve poder marcar e atribuir uma nota de 1 a 5 no **"Termômetro de Dificuldade"** (1 = Muito Difícil, 5 = Muito Fácil).

2.  **Feedback Geral da Sessão (Qualitativo - Texto):**
    - Um campo de texto `Textarea` para o terapeuta escrever livremente sobre o andamento da sessão.

3.  **Notas de Evolução do Paciente (Qualitativo - Áudio/Texto):**
    - Um componente com um botão de microfone.
    - Ao clicar, a gravação de áudio começa. Ao clicar novamente, a gravação para.
    - O áudio gravado deve ser enviado para o Supabase Storage.
    - Após o upload, o caminho do arquivo deve ser enviado para a Edge Function `transcribe-audio-note`.
    - O texto retornado pela função deve ser exibido em um campo `Textarea` abaixo do botão, permitindo que o terapeuta revise e edite a transcrição.

4.  **Botão de Salvamento:**
    - Um botão "Salvar e Concluir Sessão".
    - Ao ser clicado, ele deve chamar a Edge Function `save-session-entry`, enviando todos os dados coletados na interface: o feedback geral, a transcrição das notas de evolução, o caminho do áudio (se houver) e um array com as habilidades e seus respectivos ratings de dificuldade.

---

## FASE 2: GERAÇÃO DO RELATÓRIO COM IA

### 2.1. Edge Function (API)

Crie a Edge Function `generate-evolution-report` no diretório `supabase/functions/`. Siga a especificação detalhada no arquivo `PROGRESSO_API.md`, garantindo que ela colete todos os dados necessários (anamnese, checklist, notas qualitativas, ratings quantitativos) e os envie para um modelo de linguagem (LLM) para gerar o relatório.

### 2.2. Interface de Geração de Relatório

Na página de perfil do paciente, adicione uma nova aba chamada **"Relatórios de Evolução"**.

- Dentro desta aba, adicione:
    - Um seletor de data de início.
    - Um seletor de data de fim.
    - Um botão "Gerar Relatório".
- Ao clicar no botão, a interface deve chamar a Edge Function `generate-evolution-report` e exibir um estado de carregamento enquanto o relatório está sendo gerado.

---

## FASE 3: VISUALIZAÇÃO E EXPORTAÇÃO DO RELATÓRIO

### 3.1. Visualização e Edição

- Quando a Edge Function da Fase 2 retornar o relatório em formato Markdown, exiba-o de forma legível na tela.
- Acima do relatório exibido, adicione um botão "Editar". Ao clicar, o texto do relatório deve se tornar editável (por exemplo, dentro de um `Textarea`).

### 3.2. Exportação para PDF

- Adicione um botão "Exportar para PDF".
- Ao clicar, o conteúdo final do relatório (seja o original da IA ou o texto editado pelo profissional) deve ser convertido em um arquivo PDF e baixado pelo usuário.

**Instrução Final:** Comece pela Fase 1 e prossiga em ordem. Consulte os arquivos `.md` no repositório sempre que precisar de detalhes sobre a estrutura de dados, APIs ou plano de implementação.
