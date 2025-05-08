import streamlit as st
import pandas as pd

# --- Configuración de la página ---
st.set_page_config(page_title="Budget Tool — App Independiente", layout="wide")
st.title("📊 Budget Tool — App Independiente")

# --- 1️⃣ Definir meses del año ---
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# --- 2️⃣ Estructura de entradas por sección ---
input_structure = {
    "INBOUND ACTIVITY": [
        "Inbound Client Volume ForeCast",
        "Inbound Client AHT ForeCast",
        "Inbound Agreed Volume ForeCast",
        "Inbound Agreed AHT ForeCast",
        "NDA (%)",
        "NDS (%)",
        "Target NDS",
        "Inbound POCC (%)"
    ],
    "OUTGOING ACTIVITY": [
        "Outgoing Volume Forecast",
        "Outgoing AHT (Sec)",
        "Outgoing POCC (%)"
    ],
    "OUTBOUND ACTIVITY": [
        "Outbound Loaded Records",
        "Outbound Closing %",
        "Outbound AHT (Sec)",
        "Outbound Calls per Record (Ratio/h)",
        "Outbound Useful Contact (%)",
        "Outbound U.C Positive %",
        "Outbound POCC (%)"
    ],
    "BACKOFFICE ACTIVITY": [
        "Backoffice Volume Forecast",
        "Backoffice Volume Offered",
        "Backoffice Volume Handled",
        "Backoffice (Ratio/h)",
        "Backoffice POCC (%)"
    ],
    "EMAIL ACTIVITY": [
        "Email Volume Client Forecast",
        "Email Volume Offered",
        "Email Volume Handled",
        "Email AHT (Sec)",
        "Email POCC (%)"
    ],
    "CHAT ACTIVITY": [
        "Chat Volume Forecast",
        "Chat Offered",
        "Chat Handled",
        "Chat Concurrency",
        "Chat AHT",
        "Chat NDA (%)",
        "Chat POCC (%)"
    ],
    "SOCIAL MEDIA": [
        "S. Media Volume Forecast",
        "S. Media Offered",
        "S. Media Handled",
        "S. Media Concurrency",
        "S. Media AHT",
        "S. Media POCC (%)"
    ],
    "IN OFFICE SHRINKAGE": [
        "AUX inactivity (Hr)",
        "Aux-0 (Hr)",
        "Breaks (Hr)",
        "Lunch (Hr)",
        "Training (Hr)",
        "Training (CECO Change) (Hr)",
        "Coaching (Hr)",
        "Backup (Hr)",
        "Admin (Hr)",
        "SystemDown (Hr)"
    ],
    "OUT OFFICE SHRINKAGE": [
        "ATO - Vacations (Hr)",
        "ATO - Bank Holidays (Hr)",
        "ATO - Compensations (Hr)",
        "ATO - Compensations ETT (Hr)",
        "UATO - Absence NCNS (Hr)",
        "UATO - Absence LOAM (Hr)",
        "UATO - Absence UNIONS (Hr)"
    ],
    "CONTRACT/SEAT INFO": [
        "Average Weekly Contract",
        "Maximum Weekly Contract",
        "Peak Seat Capacity",
        "Seat Sharing Ratio"
    ],
    "REQUIRED FTE": [
        "Required Net FTEs",
        "Required Gross FTEs",
        "Approx Net Heads",
        "Approx Gross Heads",
        "Approx Calculated Seats"
    ],
    "HEADCOUNT MOVEMENTS": [
        "Production Agents (HC)",
        "Delta",
        "Delta (%)",
        "Contractual Hours Increase (HC)",
        "New Hires (HC)",
        "Movements IN (HC)",
        "Movements OUT (HC)",
        "Attrition (HC)",
        "Dismissal (HC)"
    ],
    "AGENTS ASSIGNED TO LOB": [
        "Head Count Agents",
        "Agents Assigned to LOB",
        "Initial Training Heads (Info)",
        "Initial Training Hours Paid",
        "Initial Training Hours Not Paid",
        "Attrition Pivotal (Hr)",
        "New Hires Pivotal (Hr)",
        "Dismissals Pivotal (Hr)",
        "Movements IN (1)",
        "Movements IN (2)",
        "Movements OUT (1)",
        "Movements OUT (2)",
        "Long-Term LOAMs",
        "Suspensions",
        "Unpaid Leaves",
        "Total National Holidays"
    ],
    "EXPECTED OCCUPIED SEATS": [
        "Expected Occupied Seats",
        "Holiday Hours (Concentrix)",
        "Holiday Hours (ETT)",
        "Paid Absence without Unions (Hr)",
        "Paid Absence without Unions (%)",
        "Total Estimated Cost Hours",
        "Expected Occupied Seats TM"
    ],
    "% SHIFT PATTERNS": [
        "%Diurno",
        "%Nocturno",
        "%Diurno Festivo",
        "%Nocturno Festivo"
    ]
}

# --- 3️⃣ Inicializar diccionarios de inputs ---
all_inputs = {label: [0.0]*len(months) for labels in input_structure.values() for label in labels}
single_inputs = {}
single_sections = ["CONTRACT/SEAT INFO", "EXPECTED OCCUPIED SEATS", "% SHIFT PATTERNS"]

# --- 4️⃣ Renderizar inputs en la UI ---
for section, labels in input_structure.items():
    st.subheader(section)
    if section in single_sections:
        for lbl in labels:
            single_inputs[lbl] = st.number_input(lbl, value=0.0, key=f"single_{lbl}")
    else:
        # Cabecera de tabla mensual
        cols = st.columns(len(months)+1)
        cols[0].write("**Item**")
        for i, mes in enumerate(months):
            cols[i+1].write(f"**{mes}**")
        # Filas de inputs
        for lbl in labels:
            row = st.columns(len(months)+1)
            row[0].write(lbl)
            for i, mes in enumerate(months):
                key = f"inp_{lbl}_{mes}"
                val = row[i+1].number_input(label="", value=all_inputs[lbl][i], key=key)
                all_inputs[lbl][i] = val
        # Filas de métricas calculadas para esta sección
        comp_labels = def_section_metrics.get(section, [])
        if comp_labels:
            st.write("")  # espacio
            for cl in comp_labels:
                row = st.columns(len(months)+1)
                row[0].write(f"**{cl}**")
                for i, mes in enumerate(months):
                    val = df.at[mes, cl]
                    row[i+1].write(f"{val:,.2f}")

# --- 5️⃣ Construir DataFrame de inputs mensuales ---
df = pd.DataFrame(all_inputs, index=months)

# --- 6️⃣ Definir y calcular métricas ---
# Cada métrica se define como (nombre_columna, función que recibe fila)
metrics = []
# Inbound
metrics += [
    ("Offered Calls (#)", lambda row: row["Inbound Agreed Volume ForeCast"]),
    ("Handled Calls (#)", lambda row: row["Inbound Client AHT ForeCast"] * row["Offered Calls (#)" ]),
    ("Acceptable Calls (#)", lambda row: max(0, row["Handled Calls (#)"] * row["Inbound POCC (%)"])),
    ("INBOUND TRANSACTIONAL HOURS", lambda row: row["Offered Calls (#)"] * row["Inbound AHT (Sec)"] / 3600),
    ("INBOUND PRODUCTIVE HOURS", lambda row: row["Handled Calls (#)"] - row["Acceptable Calls (#)"])
]
# Outgoing
metrics += [
    ("Outgoing Generation %", lambda row: row["Outgoing Volume Forecast"] / row["Inbound Client Volume ForeCast"] if row["Inbound Client Volume ForeCast"] else 0),
    ("OUTGOING TRANSACTIONAL HOURS", lambda row: row["Outgoing Volume Forecast"] * row["Outgoing AHT (Sec)"] / 3600),
    ("OUTGOING PRODUCTIVE HOURS", lambda row: row["Outgoing Volume Forecast"] * row["Outgoing Generation %"])
]
# Outbound
metrics += [
    ("Outbound Closed records", lambda row: row["Outbound Loaded Records"] * row["Outbound Closing %"]),
    ("OUTBOUND TRANSACTIONAL HOURS", lambda row: row["Outbound Loaded Records"] * row["Outbound AHT (Sec)"] / 3600),
    ("OUTBOUND PRODUCTIVE HOURS", lambda row: row["Outbound Closed records"] * row["Outbound Calls per Record (Ratio/h)"])
]
# Backoffice
metrics += [
    ("Backoffice Generation %", lambda row: row["Backoffice Volume Handled"] / row["Inbound Client Volume ForeCast"] if row["Inbound Client Volume ForeCast"] else 0),
    ("BACKOFFICE TRANSACTIONAL HOURS", lambda row: row["Backoffice Volume Forecast"] * row["Backoffice (Ratio/h)"] / 3600),
    ("BACKOFFICE PRODUCTIVE HOURS", lambda row: row["Backoffice Volume Handled"])
]
# Email
metrics += [
    ("EMAIL TRANSACTIONAL HOURS", lambda row: row["Email Volume Handled"] * (3600/row["Email AHT (Sec)"])/3600),
    ("EMAIL PRODUCTIVE HOURS", lambda row: row["Email Volume Handled"])
]
# Chat
metrics += [
    ("CHAT TRANSACTIONAL HOURS", lambda row: (row["Chat Volume Forecast"] * row["Chat AHT"] /3600)/ row["Chat Concurrency"]),
    ("CHAT PRODUCTIVE HOURS", lambda row: row["Chat Handled"])
]
# Social Media
metrics += [
    ("SOCIAL MEDIA TRANSACTIONAL HOURS", lambda row: (row["S. Media Volume Forecast"] * row["S. Media AHT"] /3600)/ row["S. Media Concurrency"]),
    ("SOCIAL MEDIA PRODUCTIVE HOURS", lambda row: row["S. Media Handled"])
]
# Totales
metrics += [
    ("TOTAL TRANSACTIONAL HOURS", lambda row: sum(row[col] for col, _ in metrics if "TRANSACTIONAL" in col)),
    ("TOTAL PRODUCTIVE HOURS", lambda row: sum(row[col] for col, _ in metrics if "PRODUCTIVE" in col))
]
# Shrinkages
metrics += [
    ("InOffice Shrinkage (Hr)", lambda row: sum(row[f] for f in input_structure["IN OFFICE SHRINKAGE"])),
    ("OutOffice Shrinkage (Hr)", lambda row: sum(row[f] for f in input_structure["OUT OFFICE SHRINKAGE"]))
]

# Ejecutar cálculos y añadir columnas
for name, func in metrics:
    df[name] = df.apply(func, axis=1)

# --- 7️⃣ Mostrar resultados en UI por sección ---
# Definir métricas por sección para mostrar inline
def_section_metrics = {
    "INBOUND ACTIVITY": [
        "Offered Calls (#)", "Handled Calls (#)", "Acceptable Calls (#)",
        "INBOUND TRANSACTIONAL HOURS", "INBOUND PRODUCTIVE HOURS"
    ],
    "OUTGOING ACTIVITY": [
        "Outgoing Generation %", "OUTGOING TRANSACTIONAL HOURS", "OUTGOING PRODUCTIVE HOURS"
    ],
    "OUTBOUND ACTIVITY": [
        "Outbound Closed records", "OUTBOUND TRANSACTIONAL HOURS", "OUTBOUND PRODUCTIVE HOURS"
    ],
    "BACKOFFICE ACTIVITY": [
        "Backoffice Generation %", "BACKOFFICE TRANSACTIONAL HOURS", "BACKOFFICE PRODUCTIVE HOURS"
    ],
    "EMAIL ACTIVITY": [
        "EMAIL TRANSACTIONAL HOURS", "EMAIL PRODUCTIVE HOURS"
    ],
    "CHAT ACTIVITY": [
        "CHAT TRANSACTIONAL HOURS", "CHAT PRODUCTIVE HOURS"
    ],
    "SOCIAL MEDIA": [
        "SOCIAL MEDIA TRANSACTIONAL HOURS", "SOCIAL MEDIA PRODUCTIVE HOURS"
    ],
    # Shrinkages y totales opcionales
    "": []
}

for section, labels in input_structure.items():
    if section in def_section_metrics and def_section_metrics[section]:
        st.markdown("---")
        st.subheader(f"{section} — Calculados")
        df_section = df[def_section_metrics[section]].copy()
        df_section.index.name = "Month"
        st.dataframe(df_section, use_container_width=True)

# --- 8️⃣ Mostrar valores únicos ---
if single_inputs:
    st.markdown("---")
    st.header("📋 Valores Únicos")
    for k, v in single_inputs.items():
        st.write(f"- **{k}:** {v}")

# --- 9️⃣ Exportar CSV ---
if st.button("📥 Descargar CSV"):
    csv_data = df.to_csv(index_label="Month").encode('utf-8')
    st.download_button(label="Descargar CSV", data=csv_data, file_name="budget_results.csv", mime="text/csv")

st.success("✅ App lista: estructura y fórmulas completas sin dependencias de Excel.")
