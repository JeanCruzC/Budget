import streamlit as st
import pandas as pd
import numpy as np

# Initialize session state
if 'weeks' not in st.session_state:
    st.session_state.weeks = {f'week_{i}': {} for i in range(1, 7)}

# Function to calculate metrics
def calculate_metrics(data):
    metrics = {}
    
    # Inbound Metrics
    metrics['offered_calls'] = data.get('agreed_volume_forecast', 48263)
    metrics['handled_calls'] = metrics['offered_calls'] * data.get('inbound_pocc', 55.36) / 100
    metrics['acceptable_calls'] = metrics['handled_calls'] * (1 - data.get('nds', 0) / 100)
    metrics['inbound_aht'] = data.get('agreed_aht_forecast', 654)
    metrics['inbound_availtime'] = data.get('inbound_availtime', 7072.7)
    metrics['inbound_transactional_hours'] = (metrics['handled_calls'] * metrics['inbound_aht']) / 3600
    metrics['inbound_productive_hours'] = metrics['inbound_availtime'] / data.get('productive_hours_multiplier', 68.63)
    
    # Outgoing Metrics
    metrics['outgoing_volume_forecast'] = data.get('outgoing_volume_forecast', 0)
    metrics['outgoing_generation_percent'] = 0 if metrics['offered_calls'] == 0 else (metrics['outgoing_volume_forecast'] / metrics['offered_calls']) * 100
    metrics['outgoing_aht'] = data.get('outgoing_aht', 0)
    metrics['outgoing_pocc'] = data.get('outgoing_pocc', 0)
    metrics['outgoing_availtime'] = data.get('outgoing_availtime', 0)
    metrics['outgoing_availtime_percent'] = data.get('outgoing_availtime_percent', 0)
    metrics['outgoing_transactional_hours'] = (metrics['outgoing_volume_forecast'] * metrics['outgoing_aht']) / 3600
    metrics['outgoing_productive_hours'] = metrics['outgoing_availtime'] / data.get('productive_hours_multiplier', 68.63)
    
    # Outbound Metrics
    metrics['outbound_loaded_records'] = data.get('outbound_loaded_records', 0)
    metrics['outbound_closing_percent'] = data.get('outbound_closing_percent', 0)
    metrics['outbound_closed_records'] = metrics['outbound_loaded_records'] * metrics['outbound_closing_percent'] / 100
    metrics['outbound_calls_per_record'] = data.get('outbound_calls_per_record', 0)
    metrics['outbound_calls_issued'] = metrics['outbound_closed_records'] * metrics['outbound_calls_per_record']
    metrics['outbound_useful_contact_percent'] = data.get('outbound_useful_contact_percent', 0)
    metrics['outbound_useful_records'] = metrics['outbound_calls_issued'] * metrics['outbound_useful_contact_percent'] / 100
    metrics['outbound_uc_positive_percent'] = data.get('outbound_uc_positive_percent', 0)
    metrics['outbound_uc_positive'] = metrics['outbound_useful_records'] * metrics['outbound_uc_positive_percent'] / 100
    metrics['outbound_pocc'] = data.get('outbound_pocc', 0)
    metrics['outbound_availtime'] = data.get('outbound_availtime', 0)
    metrics['outbound_availtime_percent'] = data.get('outbound_availtime_percent', 0)
    metrics['outbound_transactional_hours'] = (metrics['outbound_calls_issued'] * metrics['outbound_aht']) / 3600
    metrics['outbound_productive_hours'] = metrics['outbound_availtime'] / data.get('productive_hours_multiplier', 68.63)
    
    # Backoffice Metrics
    metrics['backoffice_volume_forecast'] = data.get('backoffice_volume_forecast', 0)
    metrics['backoffice_volume_offered'] = data.get('backoffice_volume_offered', 0)
    metrics['backoffice_volume_handled'] = data.get('backoffice_volume_handled', 0)
    metrics['backoffice_generation_percent'] = 0 if metrics['handled_calls'] == 0 else (metrics['backoffice_volume_forecast'] / metrics['handled_calls']) * 100
    metrics['backoffice_ratio'] = data.get('backoffice_ratio', 0)
    metrics['backoffice_aht'] = 3600 / metrics['backoffice_ratio'] if metrics['backoffice_ratio'] != 0 else 0
    metrics['backoffice_pocc'] = data.get('backoffice_pocc', 0)
    metrics['backoffice_availtime'] = data.get('backoffice_availtime', 0)
    metrics['backoffice_availtime_percent'] = data.get('backoffice_availtime_percent', 0)
    metrics['backoffice_transactional_hours'] = (metrics['backoffice_volume_handled'] * metrics['backoffice_aht']) / 3600
    metrics['backoffice_productive_hours'] = metrics['backoffice_availtime'] / data.get('productive_hours_multiplier', 68.63)
    
    # Email Metrics
    metrics['email_volume_forecast'] = data.get('email_volume_forecast', 0)
    metrics['email_volume_offered'] = data.get('email_volume_offered', 0)
    metrics['email_volume_handled'] = metrics['email_volume_forecast']
    metrics['email_aht_ratio'] = 3600 / data.get('email_aht', 0) if data.get('email_aht', 0) != 0 else 0
    metrics['email_aht'] = data.get('email_aht', 0)
    metrics['email_pocc'] = data.get('email_pocc', data.get('inbound_pocc', 55.36))
    metrics['email_availtime'] = data.get('email_availtime', 0)
    metrics['email_transactional_hours'] = metrics['email_volume_handled'] / metrics['email_aht_ratio'] if metrics['email_aht_ratio'] != 0 else 0
    metrics['email_productive_hours'] = metrics['email_availtime'] / data.get('productive_hours_multiplier', 68.63)
    
    # Chat Metrics
    metrics['chat_volume_forecast'] = data.get('chat_volume_forecast', 0)
    metrics['chat_offered'] = data.get('chat_offered', 0)
    metrics['chat_handled'] = data.get('chat_handled', 0)
    metrics['chat_concurrency'] = data.get('chat_concurrency', 1.00)
    metrics['chat_aht'] = data.get('chat_aht', 0)
    metrics['chat_nda'] = data.get('chat_nda', 0)
    metrics['chat_pocc'] = data.get('chat_pocc', 0)
    metrics['chat_availtime'] = data.get('chat_availtime', 0)
    
    # Prevent division by zero in chat transactional hours calculation
    if metrics['chat_concurrency'] == 0:
        metrics['chat_concurrency'] = 1.00
    
    metrics['chat_transactional_hours'] = (metrics['chat_handled'] * metrics['chat_aht'] / 3600) / metrics['chat_concurrency']
    metrics['chat_productive_hours'] = metrics['chat_availtime'] / data.get('productive_hours_multiplier', 68.63)
    
    # Social Media Metrics
    metrics['social_media_volume_forecast'] = data.get('social_media_volume_forecast', 0)
    metrics['social_media_offered'] = data.get('social_media_offered', 0)
    metrics['social_media_handled'] = data.get('social_media_handled', 0)
    metrics['social_media_concurrency'] = data.get('social_media_concurrency', 1.00)
    metrics['social_media_aht'] = data.get('social_media_aht', 942)
    metrics['social_media_availtime'] = data.get('social_media_availtime', 0)
    metrics['social_media_availtime_percent'] = data.get('social_media_availtime_percent', 0)
    metrics['social_media_pocc'] = data.get('social_media_pocc', 63.00)
    metrics['social_media_transactional_hours'] = (metrics['social_media_handled'] * metrics['social_media_aht'] / 3600) / metrics['social_media_concurrency']
    metrics['social_media_productive_hours'] = metrics['social_media_availtime'] / data.get('productive_hours_multiplier', 68.63)
    
    # Total Hours
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
    metrics['aux_inactivity_percent'] = data.get('aux_inactivity_percent', 0)
    metrics['aux_0_percent'] = data.get('aux_0_percent', 0.2)
    metrics['breaks_percent'] = data.get('breaks_percent', 2.5)
    metrics['lunch_percent'] = data.get('lunch_percent', 0)
    metrics['training_percent'] = data.get('training_percent', 4.6)
    metrics['training_ceco_percent'] = data.get('training_ceco_percent', 0)
    metrics['coaching_percent'] = data.get('coaching_percent', 1.7)
    metrics['backup_percent'] = data.get('backup_percent', 1.2)
    metrics['admin_percent'] = data.get('admin_percent', 0.2)
    metrics['systemdown_percent'] = data.get('systemdown_percent', 0)
    
    metrics['in_office_shrinkage_percent'] = sum([metrics[f] for f in [
        'aux_inactivity_percent', 'aux_0_percent', 'breaks_percent', 'lunch_percent',
        'training_percent', 'training_ceco_percent', 'coaching_percent',
        'backup_percent', 'admin_percent', 'systemdown_percent'
    ]])
    
    metrics['total_attendance_hours'] = metrics['total_productive_hours'] / (1 - metrics['in_office_shrinkage_percent'] / 100)
    
    # Calculate hours based on percentage
    metrics['aux_inactivity_hours'] = metrics['aux_inactivity_percent'] * metrics['total_attendance_hours'] / 100
    metrics['aux_0_hours'] = metrics['aux_0_percent'] * metrics['total_attendance_hours'] / 100
    metrics['breaks_hours'] = metrics['breaks_percent'] * metrics['total_attendance_hours'] / 100
    metrics['lunch_hours'] = metrics['lunch_percent'] * metrics['total_attendance_hours'] / 100
    metrics['training_hours'] = metrics['training_percent'] * metrics['total_attendance_hours'] / 100
    metrics['training_ceco_hours'] = metrics['training_ceco_percent'] * metrics['total_attendance_hours'] / 100
    metrics['coaching_hours'] = metrics['coaching_percent'] * metrics['total_attendance_hours'] / 100
    metrics['backup_hours'] = metrics['backup_percent'] * metrics['total_attendance_hours'] / 100
    metrics['admin_hours'] = metrics['admin_percent'] * metrics['total_attendance_hours'] / 100
    metrics['systemdown_hours'] = metrics['systemdown_percent'] * metrics['total_attendance_hours'] / 100
    
    metrics['in_office_shrinkage_hours'] = sum([metrics[f] for f in [
        'aux_inactivity_hours', 'aux_0_hours', 'breaks_hours', 'lunch_hours',
        'training_hours', 'training_ceco_hours', 'coaching_hours',
        'backup_hours', 'admin_hours', 'systemdown_hours'
    ]])
    
    # Out-Office Shrinkage
    metrics['ato_vacations_percent'] = data.get('ato_vacations_percent', 5.00)
    metrics['ato_bank_holidays_percent'] = data.get('ato_bank_holidays_percent', 0.00)
    metrics['ato_compensations_percent'] = data.get('ato_compensations_percent', 0.50)
    metrics['ato_compensations_ett_percent'] = data.get('ato_compensations_ett_percent', 0.00)
    metrics['uato_absence_ncns_percent'] = data.get('uato_absence_ncns_percent', 8.68)
    metrics['uato_absence_loam_percent'] = data.get('uato_absence_loam_percent', 2.76)
    metrics['uato_absence_unions_percent'] = data.get('uato_absence_unions_percent', 0.00)
    
    metrics['out_office_shrinkage_percent'] = sum([metrics[f] for f in [
        'ato_vacations_percent', 'ato_bank_holidays_percent', 'ato_compensations_percent',
        'ato_compensations_ett_percent', 'uato_absence_ncns_percent',
        'uato_absence_loam_percent', 'uato_absence_unions_percent'
    ]])
    
    metrics['total_scheduled_hours'] = metrics['total_attendance_hours'] / (1 - metrics['out_office_shrinkage_percent'] / 100)
    
    # Calculate hours based on percentage
    metrics['ato_vacations_hours'] = metrics['ato_vacations_percent'] * metrics['total_scheduled_hours'] / 100
    metrics['ato_bank_holidays_hours'] = metrics['ato_bank_holidays_percent'] * metrics['total_scheduled_hours'] / 100
    metrics['ato_compensations_hours'] = metrics['ato_compensations_percent'] * metrics['total_scheduled_hours'] / 100
    metrics['ato_compensations_ett_hours'] = metrics['ato_compensations_ett_percent'] * metrics['total_scheduled_hours'] / 100
    metrics['uato_absence_ncns_hours'] = metrics['uato_absence_ncns_percent'] * metrics['total_scheduled_hours'] / 100
    metrics['uato_absence_loam_hours'] = metrics['uato_absence_loam_percent'] * metrics['total_scheduled_hours'] / 100
    metrics['uato_absence_unions_hours'] = metrics['uato_absence_unions_percent'] * metrics['total_scheduled_hours'] / 100
    
    metrics['out_office_shrinkage_hours'] = sum([metrics[f] for f in [
        'ato_vacations_hours', 'ato_bank_holidays_hours', 'ato_compensations_hours',
        'ato_compensations_ett_hours', 'uato_absence_ncns_hours',
        'uato_absence_loam_hours', 'uato_absence_unions_hours'
    ]])
    
    # Occupancy
    metrics['pocc'] = (metrics['total_transactional_hours'] / metrics['total_productive_hours']) * 100 if metrics['total_productive_hours'] > 0 else 0
    metrics['iocc'] = (metrics['total_productive_hours'] / metrics['total_attendance_hours']) * 100 if metrics['total_attendance_hours'] > 0 else 0
    metrics['eocc'] = (metrics['total_transactional_hours'] / metrics['total_attendance_hours']) * 100 if metrics['total_attendance_hours'] > 0 else 0
    
    # Hours Agreed with Client
    metrics['total_productive_hours_agreed'] = metrics['total_productive_hours']
    metrics['total_attendance_hours_agreed'] = metrics['total_attendance_hours']
    metrics['total_scheduled_hours_agreed'] = metrics['total_scheduled_hours']
    
    # Contract/Seat Info
    metrics['weeks'] = data.get('weeks', 4.345)
    metrics['average_weekly_contract'] = metrics['total_productive_hours'] / metrics['weeks']
    metrics['maximum_weekly_contract'] = data.get('maximum_weekly_contract', 48.00)
    metrics['peak_seat_capacity'] = data.get('peak_seat_capacity', 0)
    metrics['seat_sharing_ratio'] = data.get('seat_sharing_ratio', 1.00)
