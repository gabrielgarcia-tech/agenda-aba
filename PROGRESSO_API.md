# Especificação da API (Supabase Edge Functions) - Módulo de Progresso Qualitativo (v4)

Este documento descreve as novas Edge Functions para o Módulo de Progresso Qualitativo.

## Funções

### 1. `transcribe-audio-note`

Recebe um arquivo de áudio, o transcreve e retorna o texto.

- **Método:** `POST`
- **Parâmetros:**
    - `audio_file_path`: `string` (caminho do arquivo de áudio no Supabase Storage).
- **Lógica:**
    1.  Usa um serviço de transcrição de áudio (como o `manus-speech-to-text` ou uma API externa como a do OpenAI Whisper) para converter o áudio em texto.
    2.  Retorna o texto transcrito em formato JSON: `{ "transcript": "..." }`.

### 2. `save-session-entry`

Salva a entrada completa de uma sessão (dados quantitativos e qualitativos).

- **Método:** `POST`
- **Parâmetros:**
    - `appointment_id`: `string`
    - `general_feedback`: `string`
    - `evolution_notes_transcript`: `string`
    - `evolution_notes_audio_path?`: `string` (opcional)
    - `skill_ratings`: `Array<{ skill_id: string; difficulty_rating: number }>`
- **Lógica:**
    1.  Valida as permissões do usuário.
    2.  Cria um novo registro na tabela `session_entries` com os dados qualitativos.
    3.  Para cada item no array `skill_ratings`, cria um registro na tabela `session_skill_ratings`, vinculando-o à `session_entry` recém-criada.
    4.  Retorna `{ success: true }`.

### 3. `generate-evolution-report`

O coração do sistema. Coleta todos os dados de um paciente e chama o LLM para gerar o relatório.

- **Método:** `POST`
- **Parâmetros:**
    - `patient_id`: `string`
    - `start_date`: `string` (formato YYYY-MM-DD)
    - `end_date`: `string` (formato YYYY-MM-DD)
- **Lógica:**
    1.  **Coleta de Dados:**
        - Busca a anamnese do paciente na tabela `anamnesis`.
        - Busca o checklist de habilidades do paciente.
        - Busca todas as `session_entries` para o `patient_id` dentro do período de datas, concatenando todos os `general_feedback` e `evolution_notes_transcript`.
        - Busca todos os `session_skill_ratings` no período.
    2.  **Montagem do Prompt:**
        - Constrói um prompt gigante e detalhado contendo todos os dados coletados, seguindo a estrutura definida no Plano Técnico.
    3.  **Chamada ao LLM:**
        - Envia o prompt para um modelo de linguagem avançado (ex: GPT-4, Gemini).
    4.  **Retorno:**
        - Retorna o relatório gerado pelo LLM em formato Markdown: `{ "report_markdown": "..." }`.
