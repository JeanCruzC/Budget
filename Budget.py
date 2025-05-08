import streamlit as st
import pandas as pd
import numpy as np

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = {}

# Main app title
st.title("Workforce Management Calculator")

# Sidebar for input parameters
st.sidebar.header("Input Parameters")

# Inbound Activity
st.sidebar.subheader("Inbound Activity")
with st.sidebar.expander("Inbound Activity", expanded=True):
    st.session_state.data['inbound_volume_forecast'] = st.number_input(
        "Inbound Client Volume Forecast",
        value=43876,
        step=1,
        key='inbound_volume_forecast'
    )
    st.session_state.data['inbound_aht_forecast'] = st.number_input(
        "Inbound Client AHT Forecast",
        value=615,
        step=1,
        key='inbound_aht_forecast'
    )
    st.session_state.data['agreed_volume_forecast'] = st.number_input(
        "Inbound Agreed Volume Forecast",
        value=48263,
        step=1,
        key='agreed_volume_forecast'
    )
    st.session_state.data['agreed_aht_forecast'] = st.number_input(
        "Inbound Agreed AHT Forecast",
        value=654,
        step=1,
        key='agreed_aht_forecast'
    )
    st.session_state.data['nda'] = st.number_input(
        "NDA (%)",
        value=100.00,
        step=0.01,
        key='nda'
    )
    st.session_state.data['nds'] = st.number_input(
        "NDS (%)",
        value=0.00,
        step=0.01,
        key='nds'
    )
    st.session_state.data['target_nds'] = st.number_input(
        "Target NDS",
        value=0.00,
        step=0.01,
        key='target_nds'
    )
    st.session_state.data['inbound_pocc'] = st.number_input(
        "Inbound POCC (%)",
        value=55.36,
        step=0.01,
        key='inbound_pocc'
    )

# Calculate metrics
def calculate_metrics(data):
    metrics = {}
    
    # Inbound Metrics
    metrics['offered_calls'] = data['agreed_volume_forecast']
    metrics['handled_calls'] = data['agreed_volume_forecast'] * data['inbound_pocc'] / 100
    metrics['acceptable_calls'] = metrics['handled_calls'] * (1 - data['nds'] / 100)
    metrics['inbound_aht'] = data['agreed_aht_forecast']
    metrics['inbound_availtime'] = 7072.7  # Fixed value
    metrics['inbound_transactional_hours'] = (metrics['handled_calls'] * metrics['inbound_aht']) / 3600
    metrics['inbound_productive_hours'] = metrics['inbound_availtime'] / 68.63  # Fixed value
    
    # Outgoing Metrics
    metrics['outgoing_volume_forecast'] = 0  # Default value
    metrics['outgoing_generation_percent'] = 0 if metrics['handled_calls'] == 0 else (metrics['outgoing_volume_forecast'] / metrics['handled_calls']) * 100
    metrics['outgoing_aht'] = 0  # Default value
    metrics['outgoing_pocc'] = 0  # Default value
    metrics['outgoing_availtime'] = 0  # Default value
    metrics['outgoing_transactional_hours'] = (metrics['outgoing_volume_forecast'] * metrics['outgoing_aht']) / 3600
    metrics['outgoing_productive_hours'] = metrics['outgoing_availtime'] / 68.63  # Fixed value
    
    # Outbound Metrics
    metrics['outbound_loaded_records'] = 0  # Default value
    metrics['outbound_closing_percent'] = 0.00  # Default value
    metrics['outbound_closed_records'] = metrics['outbound_loaded_records'] * metrics['outbound_closing_percent'] / 100
    metrics['outbound_calls_issued'] = metrics['outbound_loaded_records'] * 0  # Default multiplier
    metrics['outbound_aht'] = 0  # Default value
    metrics['outbound_calls_per_record'] = 0  # Default value
    metrics['outbound_useful_records'] = metrics['outbound_calls_issued'] * metrics['outbound_calls_per_record']
    metrics['outbound_useful_contact_percent'] = 0.00  # Default value
    metrics['outbound_uc_positive'] = metrics['outbound_calls_issued'] * 0  # Default multiplier
    metrics['outbound_uc_positive_percent'] = 0.00  # Default value
    metrics['outbound_pocc'] = 0.00  # Default value
    metrics['outbound_availtime'] = 0  # Default value
    metrics['outbound_transactional_hours'] = (metrics['outbound_calls_issued'] * metrics['outbound_aht']) / 3600
    metrics['outbound_productive_hours'] = metrics['outbound_availtime'] / 68.63  # Fixed value
    
    # Backoffice Metrics
    metrics['backoffice_volume_forecast'] = 0  # Default value
    metrics['backoffice_volume_offered'] = metrics['backoffice_volume_forecast']
    metrics['backoffice_volume_handled'] = metrics['backoffice_volume_forecast']
    metrics['backoffice_generation_percent'] = 0 if metrics['handled_calls'] == 0 else (metrics['backoffice_volume_forecast'] / metrics['handled_calls']) * 100
    metrics['backoffice_ratio'] = 0  # Default value
    metrics['backoffice_aht'] = 3600 / metrics['backoffice_ratio'] if metrics['backoffice_ratio'] != 0 else 0
    metrics['backoffice_pocc'] = 0.00  # Default value
    metrics['backoffice_availtime'] = 0  # Default value
    metrics['backoffice_transactional_hours'] = (metrics['backoffice_volume_handled'] * metrics['backoffice_aht']) / 3600
    metrics['backoffice_productive_hours'] = metrics['backoffice_availtime'] / 68.63  # Fixed value
    
    # Email Metrics
    metrics['email_volume_forecast'] = 0  # Default value
    metrics['email_volume_offered'] = metrics['email_volume_forecast']
    metrics['email_volume_handled'] = metrics['email_volume_forecast']
    metrics['email_aht_ratio'] = 0  # Default value
    metrics['email_aht'] = 0  # Default value
    metrics['email_availtime'] = 0  # Default value
    metrics['email_pocc'] = data['inbound_pocc']  # Using Inbound POCC
    metrics['email_transactional_hours'] = metrics['email_volume_handled'] * metrics['email_aht'] / 3600
    metrics['email_productive_hours'] = metrics['email_availtime'] / 68.63  # Fixed value
    
    # Chat Metrics
    metrics['chat_volume_forecast'] = 0  # Default value
    metrics['chat_offered'] = metrics['chat_volume_forecast']
    metrics['chat_handled'] = metrics['chat_volume_forecast']
    metrics['chat_concurrency'] = 1.00  # Default value
    metrics['chat_aht'] = 0  # Default value
    metrics['chat_nda'] = 0.00  # Default value
    metrics['chat_pocc'] = 0.00  # Default value
    metrics['chat_availtime'] = 0  # Default value
    
    # Prevent division by zero in chat transactional hours calculation
    if metrics['chat_concurrency'] == 0:
        metrics['chat_concurrency'] = 1.00
    
    metrics['chat_transactional_hours'] = (metrics['chat_handled'] * metrics['chat_aht'] / 3600) / metrics['chat_concurrency']
    metrics['chat_productive_hours'] = metrics['chat_availtime'] / 68.63  # Fixed value
    
    # Social Media Metrics
    metrics['social_media_volume_forecast'] = 0  # Default value
    metrics['social_media_offered'] = metrics['social_media_volume_forecast']
    metrics['social_media_handled'] = metrics['social_media_volume_forecast']
    metrics['social_media_concurrency'] = 1.00  # Default value
    metrics['social_media_aht'] = 942  # Fixed value
    metrics['social_media_pocc'] = 63.00  # Fixed value
    metrics['social_media_availtime'] = 0  # Default value
    metrics['social_media_transactional_hours'] = (metrics['social_media_handled'] * metrics['social_media_aht'] / 3600) / metrics['social_media_concurrency']
    metrics['social_media_productive_hours'] = metrics['social_media_availtime'] / 68.63  # Fixed value
    
    # Total Metrics
    metrics['total_transactional_hours'] = (metrics['inbound_transactional_hours'] + 
                                         metrics['outgoing_transactional_hours'] + 
                                         metrics['outbound_transactional_hours'] + 
                                         metrics['backoffice_transactional_hours'] + 
                                         metrics['email_transactional_hours'] + 
                                         metrics['chat_transactional_hours'] + 
                                         metrics['social_media_transactional_hours'])
    
    metrics['total_productive_hours'] = (metrics['inbound_productive_hours'] + 
                                       metrics['outgoing_productive_hours'] + 
                                       metrics['outbound_productive_hours'] + 
                                       metrics['backoffice_productive_hours'] + 
                                       metrics['email_productive_hours'] + 
                                       metrics['chat_productive_hours'] + 
                                       metrics['social_media_productive_hours'])
    
    # In-Office Shrinkage
    metrics['aux_inactivity_hours'] = 0  # Default value
    metrics['aux_0_hours'] = 35.34  # Fixed value
    metrics['breaks_hours'] = 441.80  # Fixed value
    metrics['lunch_hours'] = 0  # Default value
    metrics['training_hours'] = 810.83  # Fixed value
    metrics['training_ceco_hours'] = 0  # Default value
    metrics['coaching_hours'] = 300.58  # Fixed value
    metrics['backup_hours'] = 205.82  # Fixed value
    metrics['admin_hours'] = 35.34  # Fixed value
    metrics['systemdown_hours'] = 0  # Default value
    
    metrics['aux_inactivity_percent'] = 0.00  # Default value
    metrics['aux_0_percent'] = 0.20  # Fixed value
    metrics['breaks_percent'] = 2.50  # Fixed value
    metrics['lunch_percent'] = 0.00  # Default value
    metrics['training_percent'] = 4.60  # Fixed value
    metrics['training_ceco_percent'] = 0.00  # Default value
    metrics['coaching_percent'] = 1.70  # Fixed value
    metrics['backup_percent'] = 1.20  # Fixed value
    metrics['admin_percent'] = 0.20  # Fixed value
    metrics['systemdown_percent'] = 0.00  # Default value
    
    metrics['in_office_shrinkage_hours'] = sum([metrics[f] for f in [
        'aux_inactivity_hours', 'aux_0_hours', 'breaks_hours', 'lunch_hours',
        'training_hours', 'training_ceco_hours', 'coaching_hours',
        'backup_hours', 'admin_hours', 'systemdown_hours'
    ]])
    
    metrics['in_office_shrinkage_percent'] = sum([metrics[f] for f in [
        'aux_inactivity_percent', 'aux_0_percent', 'breaks_percent', 'lunch_percent',
        'training_percent', 'training_ceco_percent', 'coaching_percent',
        'backup_percent', 'admin_percent', 'systemdown_percent'
    ]])
    
    # Out-Office Shrinkage
    metrics['ato_vacations_hours'] = 1063.81  # Fixed value
    metrics['ato_bank_holidays_hours'] = 0  # Default value
    metrics['ato_compensations_hours'] = 106.38  # Fixed value
    metrics['ato_compensations_ett_hours'] = 0  # Default value
    metrics['uato_absence_ncns_hours'] = 1847.75  # Fixed value
    metrics['uato_absence_loam_hours'] = 586.22  # Fixed value
    metrics['uato_absence_unions_hours'] = 0  # Default value
    
    metrics['ato_vacations_percent'] = 5.00  # Fixed value
    metrics['ato_bank_holidays_percent'] = 0.00  # Default value
    metrics['ato_compensations_percent'] = 0.50  # Fixed value
    metrics['ato_compensations_ett_percent'] = 0.00  # Default value
    metrics['uato_absence_ncns_percent'] = 8.68  # Fixed value
    metrics['uato_absence_loam_percent'] = 2.76  # Fixed value
    metrics['uato_absence_unions_percent'] = 0.00  # Default value
    
    metrics['out_office_shrinkage_hours'] = sum([metrics[f] for f in [
        'ato_vacations_hours', 'ato_bank_holidays_hours', 'ato_compensations_hours',
        'ato_compensations_ett_hours', 'uato_absence_ncns_hours',
        'uato_absence_loam_hours', 'uato_absence_unions_hours'
    ]])
    
    metrics['out_office_shrinkage_percent'] = sum([metrics[f] for f in [
        'ato_vacations_percent', 'ato_bank_holidays_percent', 'ato_compensations_percent',
        'ato_compensations_ett_percent', 'uato_absence_ncns_percent',
        'uato_absence_loam_percent', 'uato_absence_unions_percent'
    ]])
    
    # Total Hours
    metrics['total_attendance_hours'] = metrics['total_productive_hours'] / (1 - metrics['in_office_shrinkage_percent'] / 100)
    metrics['total_scheduled_hours'] = metrics['total_attendance_hours'] / (1 - metrics['out_office_shrinkage_percent'] / 100)
    
    # Occupancy
    metrics['pocc'] = (metrics['total_transactional_hours'] / metrics['total_productive_hours']) * 100
    metrics['iocc'] = (metrics['total_productive_hours'] / metrics['total_scheduled_hours']) * 100
    metrics['eocc'] = (metrics['total_transactional_hours'] / metrics['total_scheduled_hours']) * 100
    
    # Contract/Seat Info
    metrics['maximum_weekly_contract'] = 48.00  # Fixed value
    metrics['seat_sharing_ratio'] = 1.00  # Fixed value
    
    # FTE Calculations
    metrics['required_net_ftes'] = metrics['total_attendance_hours'] / (metrics['maximum_weekly_contract'] * 4.345)  # 4.345 weeks per month
    metrics['required_gross_ftes'] = metrics['total_scheduled_hours'] / (metrics['maximum_weekly_contract'] * 4.345)
    metrics['approx_net_heads'] = metrics['required_net_ftes'] / metrics['seat_sharing_ratio']
    metrics['approx_gross_heads'] = metrics['required_gross_ftes'] / metrics['seat_sharing_ratio']
    metrics['approx_calculated_seats'] = metrics['approx_net_heads']
    
    # Attrition and Headcount
    metrics['production_agents'] = 84  # Default value
    metrics['delta'] = metrics['production_agents'] - 0 + (0 / 68.63)
    metrics['delta_percent'] = (metrics['delta'] / metrics['production_agents']) * 100
    
    metrics['contractual_hours_increase'] = 0  # Default value
    metrics['new_hires_48'] = 0  # Default value
    metrics['new_hires_24'] = 0  # Default value
    metrics['movements_in_48'] = 0  # Default value
    metrics['movements_in_24'] = 0  # Default value
    metrics['movements_out_48'] = 0  # Default value
    metrics['movements_out_24'] = 0  # Default value
    metrics['attrition_48'] = 0  # Default value
    metrics['attrition_24'] = -5  # Default value
    metrics['dismissals_48'] = 0  # Default value
    metrics['dismissals_24'] = 0  # Default value
    
    metrics['head_count_agents'] = metrics['production_agents']
    metrics['agents_assigned_to_lob'] = 89  # Default value
    metrics['initial_training_heads'] = 0  # Default value
    metrics['initial_training_hours_paid'] = 0  # Default value
    metrics['initial_training_hours_no_paid'] = 0  # Default value
    metrics['attrition'] = metrics['attrition_48'] * 0.5 + metrics['attrition_24']
    metrics['pivotal_hours'] = 0  # Default value
    metrics['new_hires'] = metrics['new_hires_48'] * 0.5 + metrics['new_hires_24']
    metrics['movements_in_1'] = metrics['movements_in_48']
    metrics['movements_in_2'] = 0  # Default value
    metrics['movements_out_1'] = metrics['movements_out_48']
    metrics['movements_out_2'] = 0  # Default value
    metrics['long_term_loams'] = 0  # Default value
    metrics['suspensions'] = 0  # Default value
    metrics['unpaid_leaves'] = 0  # Default value
    
    # Diurno and Nocturno
    metrics['diurno_percent'] = 100.00  # Default value
    metrics['nocturno_percent'] = 0.00  # Default value
    metrics['diurno_festivo_percent'] = 0.00  # Default value
    metrics['nocturno_festivo_percent'] = 0.00  # Default value
    
    return metrics

# Display results
metrics = calculate_metrics(st.session_state.data)

# Display results in vertical format
st.header("Results")

# Inbound Metrics
st.subheader("Inbound Metrics")
st.write("Offered Calls (#)", f"{metrics['offered_calls']:,}")
st.write("Handled Calls (#)", f"{metrics['handled_calls']:,}")
st.write("Acceptable Calls (#)", f"{metrics['acceptable_calls']:,}")
st.write("Inbound AHT (Sec)", f"{metrics['inbound_aht']:.2f} sec")
st.write("Inbound POCC (%)", f"{metrics['inbound_pocc']:.2f}%")

# Productivity Metrics
st.subheader("Productivity Metrics")
st.write("Transactional Hours", f"{metrics['inbound_transactional_hours']:.2f} hrs")
st.write("Productive Hours", f"{metrics['inbound_productive_hours']:.2f} hrs")

# Shrinkage
st.subheader("Shrinkage")
st.write("In-Office Shrinkage", f"{metrics['in_office_shrinkage_hours']:.2f} hrs")
st.write("Out-Office Shrinkage", f"{metrics['out_office_shrinkage_hours']:.2f} hrs")

# Occupancy
st.subheader("Occupancy")
st.write("Phone Occupancy (POCC)", f"{metrics['pocc']:.2f}%")
st.write("In-Chair Occupancy (IOCC)", f"{metrics['iocc']:.2f}%")
st.write("Effective Occupancy (EOCC)", f"{metrics['eocc']:.2f}%")

# Attrition and Headcount
st.subheader("Attrition and Headcount")
st.write("Delta", f"{metrics['delta']:.2f}")
st.write("Delta %", f"{metrics['delta_percent']:.2f}%")
st.write("Head Count Agents", f"{metrics['head_count_agents']:,}")
st.write("Agents Assigned to LOB", f"{metrics['agents_assigned_to_lob']:,}")

# Diurno and Nocturno
st.subheader("Diurno and Nocturno")
st.write("% Diurno", f"{metrics['diurno_percent']:.2f}%")
st.write("% Nocturno", f"{metrics['nocturno_percent']:.2f}%")
st.write("% Diurno Festivo", f"{metrics['diurno_festivo_percent']:.2f}%")
st.write("% Nocturno Festivo", f"{metrics['nocturno_festivo_percent']:.2f}%")

if __name__ == "__main__":
    st.write("Adjust the input parameters in the sidebar to see the results update automatically.")
