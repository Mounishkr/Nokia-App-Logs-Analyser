import json
import pandas as pd
from dateutil import parser as date_parser

def parse_logs(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    parsed_data = []
    
    if not isinstance(data, list):
        data = [data]
        
    for entry in data:
        if not isinstance(entry, dict):
            continue
            
        level = entry.get('level', 'unknown')
        timestamp_str = entry.get('timestamp', '')
        timestamp = None
        if timestamp_str:
            try:
                # Clean up " (India Standard Time)" suffix which might fail parsing
                clean_ts = timestamp_str.split('(')[0].strip()
                timestamp = date_parser.parse(clean_ts)
            except:
                pass
        
        # Determine the message
        # Sometimes it's in 'msg', sometimes 'message', sometimes in 'dev' or 'debug_info'
        message = entry.get('msg') or entry.get('message')
        
        # Get page info
        page_info = entry.get('page') or entry.get('recorded_page')
        page_name = page_info.get('pageName') if page_info else 'N/A'
        
        # Get specific details
        dev_data = entry.get('dev', {})
        debug_info = entry.get('debug_info', {})
        
        # If message not found directly, look in dev_data
        if not message and dev_data:
            message = dev_data.get('message') or dev_data.get('msg')
        if not message and debug_info:
            message = debug_info.get('message') or debug_info.get('msg')
            
        # Extract API info if available
        api_data = debug_info.get('data', {})
        
        # Initialize default values
        api_action = 'N/A'
        api_method = 'N/A'
        api_url = 'N/A'
        api_status = 'N/A'
        api_error = 'NA'
        
        if isinstance(api_data, dict):
            api_action = api_data.get('action', 'N/A')
            api_method = api_data.get('method', 'N/A')
            api_url = api_data.get('relativeUrl', 'N/A')
            api_status = api_data.get('status', 'N/A')
            api_error = api_data.get('errorResponse', 'NA')
        else:
            # If api_data is a string, use it as part of the message or just ignore it
            api_error = 'NA'
        
        # Sometimes API info is in dev_data
        if api_action == 'N/A' and isinstance(dev_data, dict):
            api_data_dev = dev_data.get('data', {})
            if isinstance(api_data_dev, dict):
                api_action = api_data_dev.get('action', api_action)
                api_status = api_data_dev.get('status', api_status)
                api_error = api_data_dev.get('error', api_error)

        parsed_data.append({
            'timestamp': timestamp,
            'level': level,
            'page_name': page_name,
            'message': str(message),
            'api_action': str(api_action),
            'api_method': str(api_method),
            'api_url': str(api_url),
            'api_status': str(api_status),
            'api_error': str(api_error),
            'full_entry': entry # Keep for detailed drill-down
        })
        
    df = pd.DataFrame(parsed_data)
    if not df.empty:
        df = df.sort_values('timestamp')
    return df
