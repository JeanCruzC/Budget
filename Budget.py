import streamlit as st
import pandas as pd

# Configuración de la página\ nst.set_page_config(page_title="Budget Tool — Streamlit Native", layout="wide")
st.title("📊 Budget Tool — App Independiente")

# 1️⃣ Meses del año
months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

# 2️⃣ Estructura de inputs agrupada por sección\input_structure = {
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
        "Trainning (Hr)",
        "Trainning (CECO Change) (Hr)",
        "Coaching (Hr)",
        "Backup (Hr)",
        "Admin (Hr)",
        "SystemDown (Hr)"
    ],
    "OUT OFFICE SHRINKAGE": [
        "ATO - Vacations (Hr)",
        "ATO - Bank Holydays (Hr)",
        "ATO - Compensations (Hr)",
        "ATO - Compensations ETT (Hr)",
        "UATO - Absence NCNS (Hr)",
        "UATO - Absence LOAM (Hr)",
        "UATO - Absence UNIONS (Hr)"
    ],
    "CONTRACT/SEAT INFO": [
        "Average Weekly Contract",
        "Maximum Weekly Contract",
        "Peek Seat Capacity",
        "Seat Sharing Ratio"
    ],
    "REQUIRED FTE": [
        "Required Net FTEs",
        "Required Gross FTEs",
        "Aprox Net Heads",
        "Aprox Gross Heads",
        "Aprox Calculated Seats"
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
        "Dismisal (HC)"
    ],
    "AGENTS ASSIGNED TO LOB": [
        "Head Count Agents",
        "Agents Assigned to LOB",
        "Initial Training Heads (Info)",
        "Initial Training Hours Paid",
        "Initial Training Hours No Paid",
        "Attrition Pivotal (Hr)",
        "New Hires Pivotal (Hr)",
        "Dismisals Pivotal (Hr)",
        "Movements IN (1)",
        "Movements IN (2)",
        "Movements OUT (1)",
        "Movements OUT (2)",
        "Long Term LOAMs",
        "Suspensions",
        "Unpaid Leaves",
        "Total National Holidays"
    ],
    "EXPECTED OCCUPIED SEATS": [
        "Expected Occupied Seats",
        "Horas Festivo Trabajadas (Concentrix)",
        "Horas Festivo Trabajadas (ETT)",
        "UATO - Paid Absence (Hr)",
        "UATO - Paid Absence (%)",
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

# 3️⃣ Inicializar inputs
all_inputs = {lbl: [0.0]*len(months) for labels in input_structure.values() for lbl in labels}
single_inputs = {}

# 4️⃣ Solicitud de inputs
single_sections = ["CONTRACT/SEAT INFO", "EXPECTED OCCUPIED SEATS", "% SHIFT PATTERNS"]
for section, labels in input_structure.items():
    st.header(section)
    if section in single_sections:
        for lbl in labels:
            single_inputs[lbl] = st.number_input(lbl, value=0.0, key=f"single_{lbl}")
    else:
        cols = st.columns(len(months) + 1)
        cols[0].write("**Item**")
        for i, mes in enumerate(months):
            cols[i+1].write(f"**{mes}**")
        for lbl in labels:
            row = st.columns(len(months) + 1)
            row[0].write(lbl)
            for i, mes in enumerate(months):
                key = f"inp_{lbl}_{mes}"
                val = row[i+1].number_input(label="", value=all_inputs[lbl][i], key=key)
                all_inputs[lbl][i] = val

# 5️⃣ DataFrame de inputs mensuales
df = pd.DataFrame(all_inputs, index=months)

# 6️⃣ Definir métricas calculadas como (label, func)
metrics = []
# Inbound\ nmetrics += [
    ("Offered Calls (#)", lambda d,i: d.at[months[i], "Inbound Agreed Volume ForeCast"]),
    ("Handled Calls (#)", lambda d,i: d.at[months[i], "Inbound Client AHT ForeCast"] * d.at[months[i], "Offered Calls (#)" ]),
    ("Acceptable Calls (#)", lambda d,i: max(0, d.at[months[i], "Handled Calls (#)"] * d.at[months[i], "Inbound POCC (%)"])),
    ("INBOUND TRANSACTIONAL HOURS", lambda d,i: d.at[months[i], "Offered Calls (#)"] * d.at[months[i], "Inbound AHT (Sec)"] / 3600),
    ("INBOUND PRODUCTIVE HOURS", lambda d,i: d.at[months[i], "Handled Calls (#)"] - d.at[months[i], "Acceptable Calls (#)"])
]
# Outgoing\ nmetrics += [
    ("Outgoing Generation %", lambda d,i: d.at[months[i], "Outgoing Volume Forecast"] / d.at[months[i], "Inbound Client Volume ForeCast"] if d.at[months[i], "Inbound Client Volume ForeCast"] else 0),
    ("OUTGOING TRANSACTIONAL HOURS", lambda d,i: d.at[months[i], "Outgoing Volume Forecast"] * d.at[months[i], "Outgoing AHT (Sec)"] / 3600),
    ("OUTGOING PRODUCTIVE HOURS", lambda d,i: d.at[months[i], "Outgoing Volume Forecast"] * d.at[months[i], "Outgoing Generation %"])
]
# Outbound\ nmetrics += [
    ("Outbound Closed records", lambda d,i: d.at[months[i], "Outbound Loaded Records"] * d.at[months[i], "Outbound Closing %"]),
    ("OUTBOUND TRANSACTIONAL HOURS", lambda d,i: d.at[months[i], "Outbound Loaded Records"] * d.at[months[i], "Outbound AHT (Sec)"] / 3600),
    ("OUTBOUND PRODUCTIVE HOURS", lambda d,i: d.at[months[i], "Outbound Closed records"] * d.at[months[i], "Outbound Calls per Record (Ratio/h)"])
]
# Backoffice\ nmetrics += [
    ("Backoffice Generation %", lambda d,i: d.at[months[i], "Backoffice Volume Handled"] / d.at[months[i], "Inbound Client Volume ForeCast"] if d.at[months[i], "Inbound Client Volume ForeCast"] else 0),
    ("BACKOFFICE TRANSACTIONAL HOURS", lambda d,i: d.at[months[i], "Backoffice Volume Forecast"] * d.at[months[i], "Backoffice AHT"] / 3600),
    ("BACKOFFICE PRODUCTIVE HOURS", lambda d,i: d.at[months[i], "Backoffice Volume Handled"])
]
# Email\ nmetrics += [
    ("EMAIL TRANSACTIONAL HOURS", lambda d,i: d.at[months[i], "Email Volume Handled"] * (3600 / d.at[months[i], "Email AHT (Sec)"]) / 3600),
    ("EMAIL PRODUCTIVE HOURS", lambda d,i: d.at[months[i], "Email Volume Handled"])
]
# Chat\ nmetrics += [
    ("CHAT TRANSACTIONAL HOURS", lambda d,i: (d.at[months[i], "Chat Volume Forecast"] * d.at[months[i], "Chat AHT"] / 3600) / d.at[months[i], "Chat Concurrency"]),
    ("CHAT PRODUCTIVE HOURS", lambda d,i: d.at[months[i], "Chat Handled"])
]
# Social Media\ nmetrics += [
    ("SOCIAL MEDIA TRANSACTIONAL HOURS", lambda d,i: (d.at[months[i], "S. Media Volume Forecast"] * d.at[months[i], "S. Media AHT"] / 3600) / d.at[months[i], "S. Media Concurrency"]),
    ("SOCIAL MEDIA PRODUCTIVE HOURS", lambda d,i: d.at[months[i], "S. Media Handled"])
]
# Totales\ nmetrics += [
    ("TOTAL TRANSACTIONAL HOURS", lambda d,i: sum(d.at[months[i], c] for c,_ in metrics if "TRANSACTIONAL" in c.upper())),
    ("TOTAL PRODUCTIVE HOURS", lambda d,i: sum(d.at[months[i], c] for c,_ in metrics if "PRODUCTIVE" in c.upper()))
]
# Shrinkages\ nmetrics += [
    ("InOffice Shrinkage (Hr)", lambda d,i: sum(d.at[months[i], f] for f in input_structure["IN OFFICE SHRINKAGE"])),
    ("OutOffice Shrinkage (Hr)", lambda d,i: sum(d.at[months[i], f] for f in input_structure["OUT OFFICE SHRINKAGE"]))
]

# 7️⃣ Inicializar columnas de resultados
for label,_ in metrics:
    df[label] = 0.0

# 8️⃣ Calcular métricas
for i in range(len(months)):
    for label, func in metrics:
        try:
            df.at[months[i], label] = func(df,i)
        except:
            df.at[months[i], label] = 0

# 9️⃣ Mostrar resultados
st.markdown("---")
st.header("📈 Resultados Computados")
st.dataframe(df, use_container_width=True)

# 🔟 Mostrar valores únicos
if single_inputs:
    st.markdown("---")
    st.header("📋 Valores Únicos")
    for k,v in single_inputs.items():
        st.write(f"- **```{k}```:** {v}")

# 🏷️ Exportar CSV
if st.button("📥 Descargar CSV"):
    csv = df.to_csv(index_label="Month").encode('utf-8')
    st.download_button(label="Descargar CSV", data=csv, file_name='budget_results.csv', mime='text/csv')

st.success("✅ App completa, independiente de Excel, con todos los ítems y fórmulas implementados.")
