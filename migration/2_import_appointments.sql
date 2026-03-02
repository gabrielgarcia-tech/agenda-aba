-- Passo 1: Criar uma tabela temporária para o CSV
CREATE TEMP TABLE temp_appointments (
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    professional_full_name TEXT,
    patient_full_name TEXT,
    appointment_type TEXT,
    is_group_appointment BOOLEAN,
    notes TEXT
);

-- Passo 2: Copiar os dados do CSV para a tabela temporária
-- Esta parte deve ser executada pela aplicação que tem acesso ao arquivo CSV.
-- Exemplo de comando com psql: \copy temp_appointments FROM 'appointments.csv' WITH (FORMAT csv, HEADER true)

-- No Supabase, você pode usar a função de importação de CSV no Storage ou uma Edge Function para ler o arquivo.
-- Para este script, vamos assumir que os dados já estão na temp_appointments.

-- Passo 3: Inserir os dados nas tabelas permanentes
DO $$
DECLARE
    rec RECORD;
    prof_id UUID;
    pat_id UUID;
    appt_id UUID;
    clinic_id_val UUID;
BEGIN
    -- Pegue o ID da primeira clínica (ajuste se houver mais de uma)
    SELECT id INTO clinic_id_val FROM clinics LIMIT 1;

    FOR rec IN SELECT * FROM temp_appointments LOOP
        -- Encontrar o ID do profissional pelo nome
        SELECT id INTO prof_id FROM profiles WHERE full_name = rec.professional_full_name LIMIT 1;

        -- Encontrar o ID do paciente pelo nome
        SELECT id INTO pat_id FROM patients WHERE name = rec.patient_full_name LIMIT 1;

        -- Se o profissional e o paciente existirem, insira o agendamento
        IF prof_id IS NOT NULL AND pat_id IS NOT NULL THEN
            -- Inserir na tabela appointments
            INSERT INTO appointments (clinic_id, start_time, end_time, appointment_type, is_group_appointment, notes, created_by)
            VALUES (clinic_id_val, rec.start_time, rec.end_time, rec.appointment_type, rec.is_group_appointment, rec.notes, auth.uid())
            RETURNING id INTO appt_id;

            -- Inserir na tabela de junção de profissionais
            INSERT INTO appointment_professionals (appointment_id, professional_id)
            VALUES (appt_id, prof_id);

            -- Inserir na tabela de junção de pacientes
            INSERT INTO appointment_patients (appointment_id, patient_id)
            VALUES (appt_id, pat_id);
        ELSE
            RAISE NOTICE 'Profissional ou Paciente não encontrado: % - %', rec.professional_full_name, rec.patient_full_name;
        END IF;
    END LOOP;
END $$;

-- Passo 4: Limpar a tabela temporária
DROP TABLE temp_appointments;
