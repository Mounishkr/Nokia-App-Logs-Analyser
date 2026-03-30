import pandas as pd
import json

class LogAnalyzer:
    def __init__(self, df):
        self.df = df
        
    def get_summary_stats(self):
        total_logs = len(self.df)
        counts = self.df['level'].value_counts().to_dict()
        return {
            'total': total_logs,
            'info': counts.get('info', 0),
            'debug': counts.get('debug', 0),
            'error': counts.get('error', 0),
            'warn': counts.get('warn', 0),
            'success_rate': self._calculate_success_rate()
        }
        
    def _calculate_success_rate(self):
        api_logs = self.df[self.df['api_action'] != 'N/A']
        if api_logs.empty:
            return 100
        
        errors = api_logs[
            (api_logs['api_status'].apply(lambda x: str(x) not in ['200', '201', 'N/A', 'NA', 'None', '0'])) |
            (api_logs['api_error'] != 'NA')
        ]
        success_rate = ((len(api_logs) - len(errors)) / len(api_logs)) * 100
        return round(success_rate, 2)
        
    def get_failing_apis(self):
        # Identify failing APIs based on status codes and error responses
        failing_logs = self.df[
            (self.df['api_action'] != 'N/A') & 
            (
                (self.df['api_status'].apply(lambda x: str(x).startswith(('4', '5')))) |
                (self.df['api_error'].apply(lambda x: x != 'NA' and x != 'NA' and 'success' not in x.lower()))
            )
        ]
        return failing_logs[['timestamp', 'page_name', 'api_action', 'api_method', 'api_url', 'api_status', 'api_error']]
        
    def get_flow_sequence(self):
        # Sequential list of pages visited and important app events
        events = []
        last_page = None
        for _, row in self.df.iterrows():
            if row['page_name'] != last_page and row['page_name'] != 'N/A':
                events.append({
                    'timestamp': row['timestamp'],
                    'type': 'PAGE_NAVIGATION',
                    'detail': row['page_name']
                })
                last_page = row['page_name']
            
            if 'App Resume' in str(row['message']):
                events.append({
                    'timestamp': row['timestamp'],
                    'type': 'APP_EVENT',
                    'detail': 'App Resumed'
                })
            elif 'App Pause' in str(row['message']):
                events.append({
                    'timestamp': row['timestamp'],
                    'type': 'APP_EVENT',
                    'detail': 'App Paused'
                })
            elif row['level'] == 'error' or (row['api_action'] != 'N/A' and self._is_error(row)):
                detail = row['api_action'] if row['api_action'] != 'N/A' else row['message']
                events.append({
                    'timestamp': row['timestamp'],
                    'type': 'ERROR',
                    'detail': detail
                })
        return pd.DataFrame(events)

    def _is_error(self, row):
        status = str(row['api_status'])
        error = str(row['api_error']).lower()
        if status.startswith(('4', '5')) or (error != 'na' and 'success' not in error):
             # Some status 0 with error details are also errors in this log format
             if status == '0' and ('failed' in error or 'error' in error or 'timeout' in error):
                 return True
             if status in ['401', '403', '500', '599']:
                 return True
        return False
