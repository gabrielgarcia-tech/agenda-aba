# Prompt para Implementação do Módulo Financeiro no Projeto ABA

> Copie e cole o conteúdo abaixo diretamente no chat do Lovable para implementar o módulo financeiro no projeto `agenda-aba`.

---

Preciso que você implemente um módulo financeiro completo no projeto `agenda-aba`. O objetivo é replicar a funcionalidade financeira já existente no meu outro projeto (`session-stream-desk`), garantindo que as estruturas de banco de dados e a interface do usuário sejam idênticas. Posteriormente, uma API de sincronização será configurada para manter os dados dos dois projetos espelhados.

Leia com atenção todas as instruções abaixo antes de escrever qualquer código.

---

## 1. BANCO DE DADOS — MIGRAÇÕES SQL

Crie um novo arquivo de migração em `supabase/migrations/` com o SQL abaixo. Este script irá criar todas as tabelas necessárias para o módulo financeiro, espelhando a estrutura do projeto `session-stream-desk`.

```sql
-- Tabela para Contas a Pagar
CREATE TABLE contas_pagar (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  franchise_id UUID REFERENCES franchises(id) ON DELETE SET NULL,
  mes INT NOT NULL,
  ano INT NOT NULL,
  dia INT NOT NULL,
  conta TEXT NOT NULL,
  valor NUMERIC(10, 2),
  categoria TEXT, -- 'fixo', 'variavel', 'parcelado'
  pagto TEXT DEFAULT 'pendente', -- 'pendente', 'pago', 'atrasado'
  parcela_atual INT,
  parcela_total INT,
  boleto TEXT,
  observacao TEXT,
  boleto_anexo_path TEXT,
  boleto_anexo_name TEXT,
  nf_path TEXT,
  nf_name TEXT,
  comprovante_path TEXT,
  comprovante_name TEXT,
  created_by UUID NOT NULL REFERENCES profiles(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE contas_pagar ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Membros da clínica podem gerenciar contas a pagar" ON contas_pagar FOR ALL USING (franchise_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid()));

-- Tabela para Entradas (Receitas)
CREATE TABLE financial_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    franchise_id UUID REFERENCES franchises(id) ON DELETE SET NULL,
    date TEXT NOT NULL, -- Armazenado como texto 'DD/MM/YYYY'
    patient_name TEXT NOT NULL,
    professional_name TEXT NOT NULL,
    sessions_count INT,
    location TEXT,
    payment_method TEXT,
    plan_type TEXT,
    amount NUMERIC(10, 2) NOT NULL,
    cpf TEXT,
    invoice_number TEXT,
    authorization_status TEXT,
    created_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE financial_entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Membros da clínica podem gerenciar entradas financeiras" ON financial_entries FOR ALL USING (franchise_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid()));

-- Tabela para Anexos das Entradas
CREATE TABLE entrada_anexos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    franchise_id UUID REFERENCES franchises(id) ON DELETE SET NULL,
    paciente TEXT NOT NULL,
    profissional TEXT NOT NULL,
    data_entrada TEXT NOT NULL,
    tipo TEXT NOT NULL, -- 'nf' ou 'comprovante'
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE entrada_anexos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Membros da clínica podem gerenciar anexos de entradas" ON entrada_anexos FOR ALL USING (franchise_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid()));

-- Tabela para Notas de Convênio
CREATE TABLE notas_convenio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    franchise_id UUID REFERENCES franchises(id) ON DELETE SET NULL,
    convenio_id UUID NOT NULL REFERENCES convenios(id),
    numero_nota TEXT NOT NULL,
    valor NUMERIC(10, 2) NOT NULL,
    data_emissao DATE NOT NULL,
    data_recebimento DATE,
    recebido BOOLEAN DEFAULT FALSE,
    observacoes TEXT,
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE notas_convenio ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Membros da clínica podem gerenciar notas de convênio" ON notas_convenio FOR ALL USING (franchise_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid()));

-- Tabela para Anexos das Notas de Convênio
CREATE TABLE nota_convenio_anexos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nota_id UUID NOT NULL REFERENCES notas_convenio(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL, -- 'nota_fiscal', 'comprovante_pagamento'
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    created_by UUID NOT NULL REFERENCES profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE nota_convenio_anexos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Membros podem gerenciar anexos de notas de convênio" ON nota_convenio_anexos FOR ALL USING (nota_id IN (SELECT id FROM notas_convenio WHERE franchise_id IN (SELECT clinic_id FROM profiles WHERE id = auth.uid())));

-- Adicionar coluna 'payment_methods' na tabela 'professionals'
ALTER TABLE professionals ADD COLUMN payment_methods TEXT[] DEFAULT '{"RPA"}';
ALTER TABLE professionals ADD COLUMN valor_clt NUMERIC(10, 2);
ALTER TABLE professionals ADD COLUMN pix_key TEXT;

```

---

## 2. FRONTEND — PÁGINAS E COMPONENTES

Agora, você deve replicar a interface do usuário do módulo financeiro. A melhor abordagem é copiar os arquivos relevantes do projeto `session-stream-desk` e adaptá-los para o `agenda-aba`.

**Instruções:**

1.  **Adicione a Rota:** No seu arquivo de rotas principal (provavelmente `App.tsx`), adicione a rota `/financeiro` que renderiza o componente `Financeiro`.

2.  **Adicione o Item de Menu:** Adicione um link para `/financeiro` no seu componente de menu lateral (`Sidebar.tsx` ou similar) com o ícone `DollarSign`.

3.  **Copie e Adapte os Arquivos:**
    - Copie a página principal: `session-stream-desk/src/pages/Financeiro.tsx` para `agenda-aba/src/pages/Financeiro.tsx`.
    - Crie o diretório `agenda-aba/src/components/financeiro/`.
    - Copie os seguintes componentes para o novo diretório:
        - `session-stream-desk/src/components/financeiro/ContasPagarTab.tsx`
        - `session-stream-desk/src/components/financeiro/EntradasTab.tsx`
        - `session-stream-desk/src/components/financeiro/RepassesTab.tsx`
        - `session-stream-desk/src/components/financeiro/NotasConvenioTab.tsx`

4.  **Copie e Adapte os Hooks:**
    - Copie o hook `session-stream-desk/src/hooks/useFinancialEntries.ts` para `agenda-aba/src/hooks/useFinancialEntries.ts`.
    - Verifique os componentes copiados por quaisquer outros hooks customizados que eles possam usar (como `useAccess`) e copie-os também, se necessário.

5.  **Adaptações e Resolução de Dependências:**
    - Após copiar os arquivos, você precisará ajustar os caminhos de importação (`@/components/...`, `@/hooks/...`, etc.) para corresponder à estrutura do projeto `agenda-aba`.
    - Instale quaisquer dependências que faltem (ex: `jspdf`, `jspdf-autotable`, `react-pdf`).
    - O código copiado usa `franchiseId` e `user` do hook `useAuth`. Certifique-se de que seu hook de autenticação no `agenda-aba` forneça informações semelhantes.

---

## 3. API DE SINCRONIZAÇÃO (INFORMATIVO)

Para sua informação, o plano de integração inclui a criação de Edge Functions e Webhooks para sincronizar os dados. **Você não precisa implementar isso agora.** Apenas saiba que a estrutura de banco de dados e frontend que você está criando será usada por este sistema de sincronização no futuro.

- **Como vai funcionar:** Um Webhook no Supabase irá detectar qualquer alteração nas tabelas financeiras e chamar uma Edge Function.
- **O que a Edge Function fará:** Ela pegará o dado alterado e fará a mesma alteração no banco de dados do projeto espelho.

Execute as Fases 1 (Banco de Dados) e 2 (Frontend) conforme descrito. A sincronização será tratada separadamente.
