# Prompt Único e Completo para Implementação do Módulo de Progresso Qualitativo com IA

> Copie e cole todo o conteúdo abaixo diretamente no chat do Lovable. Este prompt contém todas as instruções e não depende de arquivos externos.

---

**AVISO IMPORTANTE: Preserve todo o código e estrutura de arquivos existentes. Não remova, não reescreva e não substitua nenhum arquivo ou rota já criada. Apenas adicione as novas funcionalidades conforme descrito abaixo, integrando-as ao projeto `agenda-aba` existente.**

Preciso que você implemente um novo sistema de registro de progresso do paciente e geração de relatórios com IA. O objetivo é capturar dados quantitativos e qualitativos durante as sessões para que um agente de IA possa gerar relatórios de evolução completos e automáticos.

Leia com atenção todas as instruções e siga a ordem exata das fases.

---

## FASE 1: BANCO DE DADOS

Crie um novo arquivo de migração em `supabase/migrations/` e adicione o seguinte SQL para criar as novas tabelas:

### Tabela `session_entries`

```sql
CREATE TABLE session_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
  patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  professional_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  general_feedback TEXT,
  evolution_notes_audio_path TEXT,
  evolution_notes_transcript TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE session_entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own session entries" ON session_entries FOR ALL
USING (auth.uid() = professional_id);
CREATE POLICY "Admins and supervisors can view all session entries" ON session_entries FOR SELECT
USING (get_my_claim('role') IN ('"admin"', '"supervisor"', '"super_admin"'));
```

### Tabela `session_skill_ratings`

```sql
CREATE TABLE session_skill_ratings (
  session_entry_id UUID NOT NULL REFERENCES session_entries(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES patient_skills(id) ON DELETE CASCADE, -- Ajuste para o nome correto da sua tabela de habilidades do checklist
  difficulty_rating INTEGER NOT NULL,
  PRIMARY KEY (session_entry_id, skill_id)
);
ALTER TABLE session_skill_ratings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage ratings for their own session entries" ON session_skill_ratings FOR ALL
USING (session_entry_id IN (SELECT id FROM session_entries WHERE auth.uid() = professional_id));
CREATE POLICY "Admins and supervisors can view all ratings" ON session_skill_ratings FOR SELECT
USING (session_entry_id IN (SELECT id FROM session_entries WHERE get_my_claim('role') IN ('"admin"', '"supervisor"', '"super_admin"')));
```

---

## FASE 2: EDGE FUNCTIONS (API)

Crie as seguintes Edge Functions no diretório `supabase/functions/`:

### 1. `transcribe-audio-note`

- **Método:** `POST`
- **Parâmetros:** `{ "audio_file_path": "string" }`
- **Lógica:** Use um serviço de transcrição de áudio (como a API do OpenAI Whisper) para converter o áudio em texto e retorne `{ "transcript": "..." }`.

### 2. `save-session-entry`

- **Método:** `POST`
- **Parâmetros:** `{ "appointment_id": "string", "general_feedback": "string", "evolution_notes_transcript": "string", "evolution_notes_audio_path": "string", "skill_ratings": [{ "skill_id": "string", "difficulty_rating": "number" }] }`
- **Lógica:**
    1. Crie um registro em `session_entries`.
    2. Itere sobre `skill_ratings` e crie os registros correspondentes em `session_skill_ratings`.
    3. Retorne `{ "success": true }`.

### 3. `generate-evolution-report`

- **Método:** `POST`
- **Parâmetros:** `{ "patient_id": "string", "start_date": "string", "end_date": "string" }`
- **Lógica:**
    1. **Colete os dados:** Busque a anamnese, o checklist, todas as `session_entries` (concatenando as notas) e todos os `session_skill_ratings` para o paciente no período.
    2. **Monte o Prompt:** Crie um prompt detalhado para um LLM (ex: GPT-4, Gemini) com todos os dados coletados, instruindo-o a agir como um psicólogo especialista em ABA/TCC e a gerar um relatório estruturado.
    3. **Chame o LLM:** Envie o prompt para a API do modelo de linguagem.
    4. **Retorne o resultado:** Retorne o relatório gerado em Markdown: `{ "report_markdown": "..." }`.

---

## FASE 3: FRONTEND

Siga este plano para construir a interface:

### 3.1. Interface de Finalização de Sessão

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
    - Ao ser clicado, ele deve chamar a Edge Function `save-session-entry`, enviando todos os dados coletados na interface.

### 3.2. Interface de Geração de Relatório

Na página de perfil do paciente, adicione uma nova aba chamada **"Relatórios de Evolução"**.

- Dentro desta aba, adicione:
    - Um seletor de data de início.
    - Um seletor de data de fim.
    - Um botão "Gerar Relatório".
- Ao clicar no botão, a interface deve chamar a Edge Function `generate-evolution-report` e exibir um estado de carregamento enquanto o relatório está sendo gerado.

### 3.3. Visualização e Exportação do Relatório

- Quando a Edge Function da Fase 2 retornar o relatório em formato Markdown, exiba-o de forma legível na tela (use `react-markdown`).
- Acima do relatório exibido, adicione um botão "Editar". Ao clicar, o texto do relatório deve se tornar editável (por exemplo, dentro de um `Textarea`).
- Adicione um botão "Exportar para PDF". Ao clicar, o conteúdo final do relatório (seja o original da IA ou o texto editado pelo profissional) deve ser convertido em um arquivo PDF e baixado pelo usuário (use `jspdf` ou `react-to-print`).

**Instrução Final:** Comece pela Fase 1 e prossiga em ordem. Todo o plano está contido neste prompt.
