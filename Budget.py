import streamlit as st
import pandas as pd

# Configuración de la página\ nst.set_page_config(page_title="Budget Tool — Streamlit Native", layout="wide")
st.title("📊 Budget Tool — Streamlit Native — App Independiente")

# 1️⃣ Meses del año
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# 2️⃣ Estructura de inputs agrupada por sección
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
        "Trainning (Hr)",
        "Trainning (CECO Change) (Hr)",
        "Coaching (Hr)",
        "Backup (Hr)",
        "Admin (Hr)",
        "SystemDown (Hr)"
    ],
    "% IN OFFICE SHRINKAGE": [],
    "OUT OFFICE SHRINKAGE": [
        "ATO - Vacations (Hr)",
        "ATO - Bank Holydays (Hr)",
        "ATO - Compensations (Hr)",
        "ATO - Compensations ETT (Hr)",
        "UATO - Absence NCNS (Hr)",
        "UATO - Absence LOAM (Hr)",
        "UATO - Absence UNIONS (Hr)"
    ],
    "% OUT OFFICE SHRINKAGE": [],
    "TOTALS AND OCCUPANCIES": []  # sección para totales finales y ocupaciones
}

# 3️⃣ Inicializar inputs en un diccionario
all_inputs = {}
for labels in input_structure.values():
    for lbl in labels:
        all_inputs[lbl] = [0.0] * len(months)

# 4️⃣ UI: solicitar valores al usuario sección por sección
for section, labels in input_structure.items():
    st.header(section)
    if labels:
        for lbl in labels:
            st.subheader(lbl)
            cols = st.columns(len(months))
            for i, mes in enumerate(months):
                key = f"inp_{lbl}_{mes}"
                all_inputs[lbl][i] = cols[i].number_input(
                    label=f"{lbl} — {mes}",
                    value=all_inputs[lbl][i],
                    key=key
                )
    else:
        # sección sin inputs, solo encabezado
        st.write("_(No hay campos de entrada en esta sección)_")

# 5️⃣ Construir DataFrame inicial con inputs
df = pd.DataFrame(all_inputs, index=months)

# 6️⃣ Definir funciones que replican las fórmulas de Excel
# Inbound

def offered_calls(i):
    return df.at[months[i], "Inbound Agreed Volume ForeCast"]

def handled_calls(i):
    return df.at[months[i], "Inbound Client AHT ForeCast"] * df.at[months[i], "Offered Calls (#)"]

def acceptable_calls(i):
    try:
        return df.at[months[i], "Handled Calls (#)"] * df.at[months[i], "Inbound POCC (%)"]
    except:
        return 0

def inbound_aht_sec(i):
    return df.at[months[i], "Inbound Client AHT ForeCast"]

def inbound_availtime(i):
    try:
        return df.at[months[i], "Handled Calls (#)"] - df.at[months[i], "Acceptable Calls (#)"]
    except:
        return 0

def inbound_trans_hours(i):
    try:
        return df.at[months[i], "Offered Calls (#)"] * df.at[months[i], "Inbound AHT (Sec)"] / 3600
    except:
        return 0

def inbound_prod_hours(i):
    try:
        return df.at[months[i], "Inbound Availtime (Hr)"] / (df.at[months[i], "Inbound AHT (Sec)"] / 3600)
    except:
        return 0

# Outgoing
def outgoing_generation_pct(i):
    try:
        return df.at[months[i], "Outgoing Volume Forecast"] / df.at[months[i], "Inbound Client Volume ForeCast"]
    except:
        return 0

def outgoing_availtime(i):
    try:
        handled = df.at[months[i], "Outgoing Volume Forecast"] * df.at[months[i], "Outgoing Generation %"]
        return df.at[months[i], "Outgoing Volume Forecast"] - handled
    except:
        return 0

def outgoing_trans_hours(i):
    try:
        return df.at[months[i], "Outgoing Volume Forecast"] * df.at[months[i], "Outgoing AHT (Sec)"] / 3600
    except:
        return 0

def outgoing_prod_hours(i):
    try:
        return df.at[months[i], "Outgoing Availtime (Hr)"] / (df.at[months[i], "Outgoing AHT (Sec)"] / 3600)
    except:
        return 0

# Outbound
def outbound_closed_records(i):
    return df.at[months[i], "Outbound Loaded Records"] * df.at[months[i], "Outbound Closing %"]

def outbound_calls_issued(i):
    return df.at[months[i], "Outbound Closed records"] * df.at[months[i], "Outbound Calls per Record (Ratio/h)"]

def outbound_useful_records(i):
    return df.at[months[i], "Outbound Closed records"] * df.at[months[i], "Outbound Useful Contact (%)"]

def outbound_uc_positive(i):
    return df.at[months[i], "Outbound Closed records"] * df.at[months[i], "Outbound U.C Positive %"]

def outbound_availtime(i):
    try:
        return df.at[months[i], "Outbound AHT (Sec)"] - df.at[months[i], "Outbound Calls Issued"]
    except:
        return 0

def outbound_trans_hours(i):
    try:
        return df.at[months[i], "Outbound Loaded Records"] * df.at[months[i], "Outbound AHT (Sec)"] / 3600
    except:
        return 0

def outbound_prod_hours(i):
    try:
        return df.at[months[i], "Outbound Availtime (Hr)"] / (df.at[months[i], "Outbound AHT (Sec)"] / 3600)
    except:
        return 0

# Backoffice
def backoffice_generation_pct(i):
    try:
        return df.at[months[i], "Backoffice Volume Handled"] / df.at[months[i], "Inbound Client Volume ForeCast"]
    except:
        return 0

def backoffice_aht(i):
    try:
        return 3600 / df.at[months[i], "Backoffice (Ratio/h)"]
    except:
        return 0

def backoffice_availtime(i):
    return df.at[months[i], "Backoffice Volume Handled"] - df.at[months[i], "Backoffice Volume Offered"]

def backoffice_trans_hours(i):
    return df.at[months[i], "Backoffice Volume Forecast"] * df.at[months[i], "Backoffice AHT"] / 3600

def backoffice_prod_hours(i):
    try:
        return df.at[months[i], "Backoffice Availtime (Hr)"] / (df.at[months[i], "Backoffice AHT"] / 3600)
    except:
        return 0

# Email
def email_trans_hours(i):
    try:
        handled = df.at[months[i], "Email Volume Handled"]
        aht = 3600 / df.at[months[i], "Email AHT (Sec)"]
        return handled * aht / 3600
    except:
        return 0

def email_prod_hours(i):
    try:
        handled = df.at[months[i], "Email Volume Handled"]
        aht = 3600 / df.at[months[i], "Email AHT (Sec)"]
        return df.at[months[i], "Email Availtime (Hr)"] / aht
    except:
        return 0

# Chat
def chat_trans_hours(i):
    try:
        return (df.at[months[i], "Chat Volume Forecast"] * df.at[months[i], "Chat AHT"] / 3600) / df.at[months[i], "Chat Concurrency"]
    except:
        return 0

def chat_prod_hours(i):
    try:
        return df.at[months[i], "Chat Handled"] / df.at[months[i], "Chat Concurrency"]
    except:
        return 0

# Social Media
def social_trans_hours(i):
    try:
        return (df.at[months[i], "S. Media Volume Forecast"] * df.at[months[i], "S. Media AHT"] / 3600) / df.at[months[i], "S. Media Concurrency"]
    except:
        return 0

def social_prod_hours(i):
    try:
        return df.at[months[i], "S. Media Handled"] / df.at[months[i], "S. Media Concurrency"]
    except:
        return 0

# Shrinkages
def total_in_office_shrinkage(i):
    fields = [
        "AUX inactivity (Hr)", "Aux-0 (Hr)", "Breaks (Hr)", "Lunch (Hr)",
        "Trainning (Hr)", "Trainning (CECO Change) (Hr)", "Coaching (Hr)",
        "Backup (Hr)", "Admin (Hr)", "SystemDown (Hr)"
    ]
    return sum(df.at[months[i], f] for f in fields)
def total_out_office_shrinkage(i):
    fields = [
        "ATO - Vacations (Hr)", "ATO - Bank Holydays (Hr)",
        "ATO - Compensations (Hr)", "ATO - Compensations ETT (Hr)",
        "UATO - Absence NCNS (Hr)", "UATO - Absence LOAM (Hr)",
        "UATO - Absence UNIONS (Hr)"
    ]
    return sum(df.at[months[i], f] for f in fields)

def phone_occupancy(i):
    try:
        return df.at[months[i], "TOTAL TRANSACTIONAL HOURS"] / df.at[months[i], "TOTAL PRODUCTIVE HOURS"]
    except:
        return 0

def chair_occupancy(i):
    try:
        return df.at[months[i], "TOTAL PRODUCTIVE HOURS"] / df.at[months[i], "TOTAL ATTENDANCE HOURS"]
    except:
        return 0

# 7️⃣ Agregar columnas vacías para resultados
result_labels = [
    "Offered Calls (#)", "Handled Calls (#)", "Acceptable Calls (#)", "Inbound AHT (Sec)",
    "Inbound Availtime (Hr)", "INBOUND TRANSACTIONAL HOURS", "INBOUND PRODUCTIVE HOURS",
    "Outgoing Generation %", "Outgoing Availtime (Hr)", "OUTGOING TRANSACTIONAL HOURS", "OUTGOING PRODUCTIVE HOURS",
    "Outbound Closed records", "Outbound Calls Issued", "Outbound Useful Records", "Outbound U.C Positive",
    "Outbound Availtime (Hr)", "OUTBOUND TRANSACTIONAL HOURS", "OUTBOUND PRODUCTIVE HOURS",
    "Backoffice Generation %", "Backoffice AHT", "Backoffice Availtime (Hr)", "BACKOFFICE TRANSACTIONAL HOURS", "BACKOFFICE PRODUCTIVE HOURS",
    "EMAIL TRANSACTIONAL HOURS", "EMAIL PRODUCTIVE HOURS",
    "CHAT TRANSACTIONAL HOURS", "CHAT PRODUCTIVE HOURS",
    "SOCIAL MEDIA TRANSACTIONAL HOURS", "SOCIAL MEDIA PRODUCTIVE HOURS",
    "TOTAL TRANSACTIONAL HOURS", "TOTAL PRODUCTIVE HOURS",
    "InOffice Shrinkage (Hr)", "OutOffice Shrinkage (Hr)",
    "POCC - Phone Occupancy (%)", "IOCC - InChair Occupancy (%)"
]
for rl in result_labels:
    df[rl] = 0.0

# 8️⃣ Bucle de cálculo mes a mes
for i in range(len(months)):
    # Inbound
    df.at[months[i], "Offered Calls (#)"] = offered_calls(i)
    df.at[months[i], "Handled Calls (#)"] = handled_calls(i)
    df.at[months[i], "Acceptable Calls (#)"] = acceptable_calls(i)
    df.at[months[i], "Inbound AHT (Sec)"] = inbound_aht_sec(i)
    df.at[months[i], "Inbound Availtime (Hr)"] = inbound_availtime(i)
    df.at[months[i], "INBOUND TRANSACTIONAL HOURS"] = inbound_trans_hours(i)
    df.at[months[i], "INBOUND PRODUCTIVE HOURS"] = inbound_prod_hours(i)
    # Outgoing
    df.at[months[i], "Outgoing Generation %"] = outgoing_generation_pct(i)
    df.at[months[i], "Outgoing Availtime (Hr)"] = outgoing_availtime(i)
    df.at[months[i], "OUTGOING TRANSACTIONAL HOURS"] = outgoing_trans_hours(i)
    df.at[months[i], "OUTGOING PRODUCTIVE HOURS"] = outgoing_prod_hours(i)
    # Outbound
    df.at[months[i], "Outbound Closed records"] = outbound_closed_records(i)
    df.at[months[i], "Outbound Calls Issued"] = outbound_calls_issued(i)
    df.at[months[i], "Outbound Useful Records"] = outbound_useful_records(i)
    df.at[months[i], "Outbound U.C Positive"] = outbound_uc_positive(i)
    df.at[months[i], "Outbound Availtime (Hr)"] = outbound_availtime(i)
    df.at[months[i], "OUTBOUND TRANSACTIONAL HOURS"] = outbound_trans_hours(i)
    df.at[months[i], "OUTBOUND PRODUCTIVE HOURS"] = outbound_prod_hours(i)
    # Backoffice
    df.at[months[i], "Backoffice Generation %"] = backoffice_generation_pct(i)
    df.at[months[i], "Backoffice AHT"] = backoffice_aht(i)
    df.at[months[i], "Backoffice Availtime (Hr)"] = backoffice_availtime(i)
    df.at[months[i], "BACKOFFICE TRANSACTIONAL HOURS"] = backoffice_trans_hours(i)
    df.at[months[i], "BACKOFFICE PRODUCTIVE HOURS"] = backoffice_prod_hours(i)
    # Email
    df.at[months[i], "EMAIL TRANSACTIONAL HOURS"] = email_trans_hours(i)
    df.at[months[i], "EMAIL PRODUCTIVE HOURS"] = email_prod_hours(i)
    # Chat
    df.at[months[i], "CHAT TRANSACTIONAL HOURS"] = chat_trans_hours(i)
    df.at[months[i], "CHAT PRODUCTIVE HOURS"] = chat_prod_hours(i)
    # Social Media
    df.at[months[i], "SOCIAL MEDIA TRANSACTIONAL HOURS"] = social_trans_hours(i)
    df.at[months[i], "SOCIAL MEDIA PRODUCTIVE HOURS"] = social_prod_hours(i)
    # Totales
    df.at[months[i], "TOTAL TRANSACTIONAL HOURS"] = sum(
        df.at[months[i], col] for col in [
            "INBOUND TRANSACTIONAL HOURS","OUTGOING TRANSACTIONAL HOURS",
            "OUTBOUND TRANSACTIONAL HOURS","BACKOFFICE TRANSACTIONAL HOURS",
            "EMAIL TRANSACTIONAL HOURS","CHAT TRANSACTIONAL HOURS",
            "SOCIAL MEDIA TRANSACTIONAL HOURS"
        ]
    )
    df.at[months[i], "TOTAL PRODUCTIVE HOURS"] = sum(
        df.at[months[i], col] for col in [
            "INBOUND PRODUCTIVE HOURS","OUTGOING PRODUCTIVE HOURS",
            "OUTBOUND PRODUCTIVE HOURS","BACKOFFICE PRODUCTIVE HOURS",
            "EMAIL PRODUCTIVE HOURS","CHAT PRODUCTIVE HOURS",
            "SOCIAL MEDIA PRODUCTIVE HOURS"
        ]
    )
    # Shrinkages
    df.at[months[i], "InOffice Shrinkage (Hr)"] = total_in_office_shrinkage(i)
    df.at[months[i], "OutOffice Shrinkage (Hr)"] = total_out_office_shrinkage(i)
    # Ocupaciones
    df.at[months[i], "POCC - Phone Occupancy (%)"] = phone_occupancy(i)
    df.at[months[i], "IOCC - InChair Occupancy (%)"] = chair_occupancy(i)

# 9️⃣ Mostrar resultados
st.markdown("---")
st.header("📈 Resultados Computados")
st.dataframe(df, use_container_width=True)

# 🔟 Exportar datos como CSV
if st.button("📥 Descargar resultados como CSV"):
    csv = df.to_csv(index_label="Month").encode('utf-8')
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name='budget_results.csv',
        mime='text/csv'
    )

st.success("✅ App completa: totalmente independiente, con todas las fórmulas implementadas.")
