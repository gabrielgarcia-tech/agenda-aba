# Especificação do Banco de Dados - Módulo de Progresso Qualitativo (v4)

Este documento detalha as novas tabelas necessárias para suportar a captura de dados qualitativos e quantitativos em sessão, permitindo a geração de relatórios de evolução com IA.

## Novas Tabelas (v4)

### 1. `session_entries`

Armazena os dados qualitativos de cada sessão finalizada.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `uuid` | Chave Primária (PK) |
| `appointment_id` | `uuid` | FK para `appointments.id`, identificando a sessão |
| `patient_id` | `uuid` | FK para `patients.id` |
| `professional_id` | `uuid` | FK para `profiles.id` |
| `general_feedback` | `text` | Texto do "Feedback Geral da Sessão" |
| `evolution_notes_audio_path` | `text` | Caminho para o arquivo de áudio no Supabase Storage |
| `evolution_notes_transcript` | `text` | Transcrição do áudio, editável pelo terapeuta |
| `created_at` | `timestamptz` | Data e hora do registro |

**Políticas de RLS:**
- Apenas o profissional que realizou a sessão e administradores/supervisores podem criar e ler as entradas.

### 2. `session_skill_ratings`

Armazena os dados quantitativos (ratings de dificuldade) para as habilidades trabalhadas em sessão.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `session_entry_id` | `uuid` | PK, FK para `session_entries.id` |
| `skill_id` | `uuid` | PK, FK para a tabela de habilidades do checklist do paciente |
| `difficulty_rating` | `integer` | Nota de 1 a 5 (Termômetro de Dificuldade) |

**Políticas de RLS:**
- Acesso vinculado à permissão de leitura da `session_entries` correspondente.
