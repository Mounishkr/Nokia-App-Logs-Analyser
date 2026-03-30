from parser import parse_logs
from analyzer import LogAnalyzer
import os

def test_analysis():
    log_file = "app_logs_2026-03-27_1774619308147.json"
    if not os.path.exists(log_file):
        print("Log file not found.")
        return
        
    print(f"--- Analysis for {log_file} ---")
    df = parse_logs(log_file)
    analyzer = LogAnalyzer(df)
    
    stats = analyzer.get_summary_stats()
    print(f"Stats: {stats}")
    
    failures = analyzer.get_failing_apis()
    print(f"\nFailing APIs ({len(failures)}):")
    if not failures.empty:
        # Display unique failing actions for brevity in test output
        print(failures[['api_action', 'api_status', 'api_url']].drop_duplicates())
    
    flow = analyzer.get_flow_sequence()
    print(f"\nFlow Events: {len(flow)}")
    if not flow.empty:
        print("Flow Summary:")
        # Show first 10 events
        print(flow.head(10))

if __name__ == "__main__":
    test_analysis()
