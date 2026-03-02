"""
Script para processar a planilha AgendaProfissionais.xlsx e gerar o CSV de migração
no formato de RECORRÊNCIA SEMANAL.

Cada linha representa uma regra recorrente:
- day_of_week: 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta
- start_time: horário de início (HH:MM)
- end_time: horário de fim (HH:MM)
- professional_full_name: nome completo do profissional
- patient_full_name: nome completo do paciente
- appointment_type: clinic | school | home | online
- notes: observações (ex: Horário divergente)

A plataforma usa essas regras para gerar os agendamentos automaticamente
para os próximos meses, respeitando a recorrência semanal.
"""
import openpyxl
import csv
import re

# Mapeamento de dias da semana para número (0=segunda, 4=sexta)
DAYS = {
    'SEGUNDA-FEIRA': 0,
    'TERÇA-FEIRA': 1,
    'QUARTA-FEIRA': 2,
    'QUINTA-FEIRA': 3,
    'SEXTA-FEIRA': 4,
}

DAY_NAMES_PT = {
    0: 'segunda-feira',
    1: 'terça-feira',
    2: 'quarta-feira',
    3: 'quinta-feira',
    4: 'sexta-feira',
}

def parse_horario(horario_str):
    """Converte '08h00 - 08h50' em (hora_inicio, minuto_inicio, hora_fim, minuto_fim)"""
    if not horario_str:
        return None
    match = re.match(r'(\d{2})h(\d{2})\s*-\s*(\d{2})h(\d{2})', str(horario_str))
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
    return None

def clean_name(name):
    """Remove espaços extras, sufixos de especialidade e normaliza o nome."""
    if not name:
        return None
    name = str(name).strip()
    # Remover sufixos como '- PSICO', '- FONO', '- TO', '- ABA'
    name = re.sub(r'\s*-\s*(PSICO|FONO|TO|ABA|PSICOLOGIA|FONOAUDIOLOGIA)\s*$', '', name, flags=re.IGNORECASE)
    return name.strip()

def extract_professional_name(sheet_name):
    """Extrai o nome do profissional do nome da aba."""
    match = re.match(r'^(.+?)\s*[\(\(]', sheet_name)
    if match:
        return match.group(1).strip()
    return sheet_name.strip()

def process_cell(cell_value, horario_parsed, day_of_week, professional_name):
    """
    Processa o conteúdo de uma célula e retorna uma lista de regras de recorrência.
    """
    if not cell_value:
        return []

    value = str(cell_value).strip()

    # Ignorar células vazias, VAGO, SUPERVISÃO, Saída, etc.
    skip_keywords = ['VAGO', 'SUPERVISÃO', 'SUPERVISAO', 'Saída', 'Saida', 'FOLGA', 'FERIADO']
    if any(kw.lower() in value.lower() for kw in skip_keywords):
        return []

    if not horario_parsed:
        return []

    h_start, m_start, h_end, m_end = horario_parsed

    # Detectar horário divergente: "Das HHhMM às HHhMM Nome"
    divergent_match = re.match(r'Das?\s+(\d{1,2})h(\d{2})\s+[àa]s?\s+(\d{1,2})h(\d{2})\s*[-–]?\s*(.+)', value, re.IGNORECASE)
    if divergent_match:
        h_start = int(divergent_match.group(1))
        m_start = int(divergent_match.group(2))
        h_end = int(divergent_match.group(3))
        m_end = int(divergent_match.group(4))
        patient_name = clean_name(divergent_match.group(5))
        return [{
            'day_of_week': day_of_week,
            'day_of_week_name': DAY_NAMES_PT[day_of_week],
            'start_time': f'{h_start:02d}:{m_start:02d}',
            'end_time': f'{h_end:02d}:{m_end:02d}',
            'professional_full_name': professional_name,
            'patient_full_name': patient_name,
            'appointment_type': 'clinic',
            'notes': 'Horário divergente',
        }]

    # Detectar atendimento escolar: "Atendimento Escolar: Nome"
    school_match = re.match(r'Atendimento Escolar[:\s]+(.+)', value, re.IGNORECASE)
    if school_match:
        patient_name = clean_name(school_match.group(1))
        return [{
            'day_of_week': day_of_week,
            'day_of_week_name': DAY_NAMES_PT[day_of_week],
            'start_time': f'{h_start:02d}:{m_start:02d}',
            'end_time': f'{h_end:02d}:{m_end:02d}',
            'professional_full_name': professional_name,
            'patient_full_name': patient_name,
            'appointment_type': 'school',
            'notes': 'Atendimento Escolar',
        }]

    # Atendimento normal
    patient_name = clean_name(value)
    if not patient_name or len(patient_name) < 3:
        return []

    return [{
        'day_of_week': day_of_week,
        'day_of_week_name': DAY_NAMES_PT[day_of_week],
        'start_time': f'{h_start:02d}:{m_start:02d}',
        'end_time': f'{h_end:02d}:{m_end:02d}',
        'professional_full_name': professional_name,
        'patient_full_name': patient_name,
        'appointment_type': 'clinic',
        'notes': '',
    }]


def process_sheet(ws, professional_name):
    """Processa uma aba de profissional e retorna lista de regras de recorrência."""
    appointments = []

    # Encontrar a linha do cabeçalho (SEGUNDA-FEIRA, ...)
    header_row = None
    day_columns = {}  # col_index -> day_of_week

    for row in ws.iter_rows():
        for cell in row:
            if cell.value and str(cell.value).strip() == 'SEGUNDA-FEIRA':
                header_row = cell.row
                for c in ws.iter_cols(min_row=header_row, max_row=header_row, min_col=1, max_col=ws.max_column):
                    for hcell in c:
                        day_name = str(hcell.value).strip() if hcell.value else ''
                        if day_name in DAYS:
                            day_columns[hcell.column] = DAYS[day_name]
                break
        if header_row:
            break

    if not header_row or not day_columns:
        print(f"  [AVISO] Não encontrou cabeçalho em: {professional_name}")
        return []

    # Encontrar coluna de horários
    horario_col = 1

    # Processar linhas de dados
    for row in ws.iter_rows(min_row=header_row + 1):
        horario_cell = None
        for cell in row:
            if cell.column == horario_col:
                horario_cell = cell
                break

        if not horario_cell or not horario_cell.value:
            continue

        horario_str = str(horario_cell.value).strip()
        horario_parsed = parse_horario(horario_str)

        if not horario_parsed:
            continue

        for col_idx, day_of_week in day_columns.items():
            cell_value = None
            for cell in row:
                if cell.column == col_idx:
                    cell_value = cell.value
                    break

            appts = process_cell(cell_value, horario_parsed, day_of_week, professional_name)
            appointments.extend(appts)

    return appointments


def main():
    wb = openpyxl.load_workbook('/home/ubuntu/upload/AgendaProfissionais.xlsx', data_only=True)

    skip_sheets = {'Atendimentos', 'Cópia de Modelo'}

    all_appointments = []

    for sheet_name in wb.sheetnames:
        if sheet_name in skip_sheets:
            continue

        ws = wb[sheet_name]
        professional_name = extract_professional_name(sheet_name)
        print(f"Processando: {professional_name}")

        appts = process_sheet(ws, professional_name)
        print(f"  -> {len(appts)} regras de recorrência encontradas")
        all_appointments.extend(appts)

    print(f"\nTotal de regras de recorrência: {len(all_appointments)}")

    # Salvar CSV
    output_path = '/home/ubuntu/agenda-aba/migration/recurring_appointments.csv'
    fieldnames = ['day_of_week', 'day_of_week_name', 'start_time', 'end_time',
                  'professional_full_name', 'patient_full_name', 'appointment_type', 'notes']

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_appointments)

    print(f"CSV salvo em: {output_path}")

    # Amostra
    print("\n--- Amostra dos primeiros 10 registros ---")
    for appt in all_appointments[:10]:
        print(appt)

    # Estatísticas
    professionals = set(a['professional_full_name'] for a in all_appointments)
    patients = set(a['patient_full_name'] for a in all_appointments)
    school = [a for a in all_appointments if a['appointment_type'] == 'school']
    divergent = [a for a in all_appointments if 'divergente' in a['notes'].lower()]

    by_day = {}
    for a in all_appointments:
        d = a['day_of_week_name']
        by_day[d] = by_day.get(d, 0) + 1

    print(f"\n--- Estatísticas ---")
    print(f"Profissionais únicos: {len(professionals)}")
    print(f"Pacientes únicos: {len(patients)}")
    print(f"Atendimentos escolares: {len(school)}")
    print(f"Horários divergentes: {len(divergent)}")
    print(f"Por dia da semana:")
    for day in ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira']:
        print(f"  {day}: {by_day.get(day, 0)}")


if __name__ == '__main__':
    main()
