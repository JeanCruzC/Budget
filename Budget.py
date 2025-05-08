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
# Secciones sin dimensión mensual
single_sections = ["CONTRACT/SEAT INFO", "EXPECTED OCCUPIED SEATS", "% SHIFT PATTERNS"]

# --- 3️⃣ Inicializar inputs ---
all_inputs = {label: [0.0] * len(months) for sect in input_structure.values() for label in sect}
single_inputs = {}

# --- 4️⃣ Renderizar entradas ---
for section, labels in input_structure.items():
    st.subheader(section)
    if section in single_sections:
        for lbl in labels:
            single_inputs[lbl] = st.number_input(lbl, key=f"single_{lbl}", value=0.0)
    else:
        cols = st.columns(len(months) + 1)
        cols[0].write("**Item**")
        for i, m in enumerate(months):
            cols[i+1].write(f"**{m}**")
        for lbl in labels:
            row = st.columns(len(months) + 1)
            row[0].write(lbl)
            for i, m in enumerate(months):
                key = f"inp_{lbl}_{m}"
                val = row[i+1].number_input("", key=key, value=all_inputs[lbl][i])
                all_inputs[lbl][i] = val

# --- 5️⃣ Construir DataFrame ---
df = pd.DataFrame(all_inputs, index=months)

# Copiar a columna estándar para fórmulas
if "Inbound Agreed AHT ForeCast" in df.columns:
    df["Inbound AHT (Sec)"] = df["Inbound Agreed AHT ForeCast"]

# --- 6️⃣ Definir métricas y calcularlas ---
metrics = []
# Inbound
metrics += [
    ("Offered Calls (#)", lambda r: r["Inbound Agreed Volume ForeCast"]),
    ("Handled Calls (#)", lambda r: r["Offered Calls (#)"] * r["Inbound AHT (Sec)" ]),
    ("Acceptable Calls (#)", lambda r: max(0, r["Handled Calls (#)"] * r["Inbound POCC (%)"])),
    ("INBOUND TRANSACTIONAL HOURS", lambda r: r["Offered Calls (#)"] * r["Inbound AHT (Sec)"] / 3600),
    ("INBOUND PRODUCTIVE HOURS", lambda r: r["Handled Calls (#)"] - r["Acceptable Calls (#)"])
]
# Outgoing
metrics += [
    ("Outgoing Generation %", lambda r: r["Outgoing Volume Forecast"] / r.get("Inbound Client Volume ForeCast", 1) if r.get("Inbound Client Volume ForeCast", 0) else 0),
    ("OUTGOING TRANSACTIONAL HOURS", lambda r: r["Outgoing Volume Forecast"] * r["Outgoing AHT (Sec)"] / 3600),
    ("OUTGOING PRODUCTIVE HOURS", lambda r: r["Outgoing Volume Forecast"] * r["Outgoing Generation %"])
]
# Outbound
metrics += [
    ("Outbound Closed records", lambda r: r["Outbound Loaded Records"] * r["Outbound Closing %"]),
    ("OUTBOUND TRANSACTIONAL HOURS", lambda r: r["Outbound Loaded Records"] * r["Outbound AHT (Sec)"] / 3600),
    ("OUTBOUND PRODUCTIVE HOURS", lambda r: r["Outbound Closed records"] * r["Outbound Calls per Record (Ratio/h)"])
]
# Backoffice
metrics += [
    ("Backoffice Generation %", lambda r: r["Backoffice Volume Handled"] / r.get("Inbound Agreed Volume ForeCast", 1) if r.get("Inbound Agreed Volume ForeCast", 0) else 0),
    ("BACKOFFICE TRANSACTIONAL HOURS", lambda r: r["Backoffice Volume Forecast"] * r["Backoffice (Ratio/h)"] / 3600),
    ("BACKOFFICE PRODUCTIVE HOURS", lambda r: r["Backoffice Volume Handled"])
]
# Email
metrics += [
    ("EMAIL TRANSACTIONAL HOURS", lambda r: r["Email Volume Handled"] * (3600 / r["Email AHT (Sec)"]) / 3600 if r.get("Email AHT (Sec)", 0) else 0),
    ("EMAIL PRODUCTIVE HOURS", lambda r: r["Email Volume Handled"])
]
# Chat
metrics += [
    ("CHAT TRANSACTIONAL HOURS", lambda r: (r["Chat Volume Forecast"] * r["Chat AHT"] / 3600) / r.get("Chat Concurrency", 1) if r.get("Chat Concurrency", 0) else 0),
    ("CHAT PRODUCTIVE HOURS", lambda r: r["Chat Handled"])
]
# Social Media
metrics += [
    ("SOCIAL MEDIA TRANSACTIONAL HOURS", lambda r: (r["S. Media Volume Forecast"] * r["S. Media AHT"] / 3600) / r.get("S. Media Concurrency", 1) if r.get("S. Media Concurrency", 0) else 0),
    ("SOCIAL MEDIA PRODUCTIVE HOURS", lambda r: r["S. Media Handled"])
]
# Totales
metrics += [
    ("TOTAL TRANSACTIONAL HOURS", lambda r: sum(r[c] for c, _ in metrics if "TRANSACTIONAL" in c)),
    ("TOTAL PRODUCTIVE HOURS", lambda r: sum(r[c] for c, _ in metrics if "PRODUCTIVE" in c))
]
# Shrinkages
metrics += [
    ("InOffice Shrinkage (Hr)", lambda r: sum(r[f] for f in input_structure["IN OFFICE SHRINKAGE"])),
    ("OutOffice Shrinkage (Hr)", lambda r: sum(r[f] for f in input_structure["OUT OFFICE SHRINKAGE"]))
]
# Ejecutar cálculos
for name, func in metrics:
    df[name] = df.apply(func, axis=1)

# --- 7️⃣ Mostrar métricas por sección ---
def_section_metrics = {
    "INBOUND ACTIVITY": ["Offered Calls (#)", "Handled Calls (#)", "Acceptable Calls (#)", "INBOUND TRANSACTIONAL HOURS", "INBOUND PRODUCTIVE HOURS"],
    "OUTGOING ACTIVITY": ["Outgoing Generation %", "OUTGOING TRANSACTIONAL HOURS", "OUTGOING PRODUCTIVE HOURS"],
    "OUTBOUND ACTIVITY": ["Outbound Closed records", "OUTBOUND TRANSACTIONAL HOURS", "OUTBOUND PRODUCTIVE HOURS"],
    "BACKOFFICE ACTIVITY": ["Backoffice Generation %", "BACKOFFICE TRANSACTIONAL HOURS", "BACKOFFICE PRODUCTIVE HOURS"],
    "EMAIL ACTIVITY": ["EMAIL TRANSACTIONAL HOURS", "EMAIL PRODUCTIVE HOURS"],
    "CHAT ACTIVITY": ["CHAT TRANSACTIONAL HOURS", "CHAT PRODUCTIVE HOURS"],
    "SOCIAL MEDIA": ["SOCIAL MEDIA TRANSACTIONAL HOURS", "SOCIAL MEDIA PRODUCTIVE HOURS"]
}
for section, labs in def_section_metrics.items():
    st.markdown("---")
    st.subheader(f"{section} — Calculados")
    df_sec = df[labs].copy()
    df_sec.index.name = "Month"
    st.dataframe(df_sec, use_container_width=True)

# --- 8️⃣ Valores únicos ---
if single_inputs:
    st.markdown("---")
    st.header("📋 Valores Únicos")
    for k, v in single_inputs.items():
        st.write(f"- **{k}:** {v}")

# --- 9️⃣ Export CSV ---
if st.button("📥 Descargar CSV"):
    csv = df.to_csv(index_label="Month").encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="budget_results.csv", mime="text/csv")

st.success("✅ App lista: estructura y fórmulas completas sin dependencias de Excel.")
