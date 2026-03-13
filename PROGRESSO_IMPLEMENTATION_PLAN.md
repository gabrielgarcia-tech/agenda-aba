# Plano de Implementação - Módulo de Progresso Qualitativo (v4)

Este documento descreve o plano para implementar o novo sistema de captura de progresso e geração de relatórios com IA.

## Fases

### Fase 1: Backend e Captura de Dados (1-2 semanas)

1.  **[ ] Migração do Banco de Dados:**
    - Criar um novo arquivo de migração SQL para adicionar as tabelas `session_entries` e `session_skill_ratings`, conforme `PROGRESSO_DATABASE.md`.

2.  **[ ] Desenvolvimento das Edge Functions:**
    - Implementar a função `transcribe-audio-note`.
    - Implementar a função `save-session-entry`.

3.  **[ ] Interface de Finalização de Sessão:**
    - Criar uma nova página/modal que aparece ao finalizar uma sessão na agenda.
    - Implementar o componente para selecionar habilidades e atribuir o "Termômetro de Dificuldade" (1-5).
    - Implementar o campo de texto para o "Feedback Geral".
    - Implementar o componente de gravação de áudio:
        - Botão para iniciar/parar a gravação.
        - Ao parar, o áudio é enviado para o Supabase Storage.
        - O caminho do arquivo é enviado para a Edge Function `transcribe-audio-note`.
        - O texto retornado é exibido em um `Textarea` para edição.
    - O botão "Salvar Sessão" chama a Edge Function `save-session-entry` com todos os dados coletados.

### Fase 2: Backend e Frontend do Agente de IA (1 semana)

1.  **[ ] Desenvolvimento da Edge Function Principal:**
    - Implementar a Edge Function `generate-evolution-report`, que orquestra a coleta de dados e a chamada ao LLM.

2.  **[ ] Interface de Geração de Relatório:**
    - Na página de detalhes do paciente, adicionar uma nova aba "Relatórios de Evolução".
    - Nesta aba, adicionar seletores de data ("De" e "Até") e um botão "Gerar Relatório".
    - Ao clicar no botão, chamar a Edge Function `generate-evolution-report` e exibir um indicador de carregamento.

### Fase 3: Visualização e Edição do Relatório (1 semana)

1.  **[ ] Componente de Visualização:**
    - Quando a Edge Function retornar o relatório em Markdown, exibi-lo em um componente que renderiza Markdown para HTML (ex: `react-markdown`).

2.  **[ ] Funcionalidade de Edição:**
    - Adicionar um botão "Editar" que transforma o visualizador de Markdown em um editor de texto (ex: um `Textarea` com o conteúdo Markdown).
    - Permitir que o profissional faça ajustes finos no texto gerado pela IA.

3.  **[ ] Exportação para PDF:**
    - Implementar um botão "Exportar para PDF" que converte o conteúdo final (editado ou não) do relatório em um arquivo PDF para download, usando uma biblioteca como `jspdf` ou `react-to-print`.
