# 🔍 App Log Insight: Production Log Analyzer

App Log Insight is a high-performance log analyzer specifically designed to parse and visualize production logs for mobile and web applications. It specializes in tracing API failures, reconstructing user flows, and providing a modern dashboard for root cause analysis.

## ✨ Key Features

- **📊 Unified Dashboard**: High-level statistics on log levels, event distribution, and API success rates.
- **🚫 Error Tracing**: Deep-dive analysis of failing APIs with automatic correlation of status codes and error responses.
- **🔄 Interaction Flow Reconstruction**: Vertical timeline of page navigations and crucial system events (App Resume, Pause, Errors).
- **📋 Log Explorer**: Advanced filtering and searching across massive log files with JSON drill-down capability.
- **🕒 Timeline Visualization**: Graphical representation of system health over time.

## 🛠 Tech Stack

- **Streamlit**: Core web framework for interactive UI.
- **Pandas**: Efficient log processing and data manipulation.
- **Plotly**: Dynamic, responsive data visualizations.
- **Python-Dateutil**: Robust timestamp parsing.

## 🚀 Getting Started

1. **Clone the repository**:
   ```bash
   git clone <your-repo-link>
   cd app-logs-analyzer
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

4. **Upload your log file**:
   Select your JSON log file from the sidebar to begin analysis.

## 📁 Log Format Support

The analyzer supports standard JSON log arrays with the following key fields:
- `level`: (info, debug, error, warn)
- `timestamp`: (ISO or standard date formats)
- `page/recorded_page`: (Contextual page information)
- `dev/debug_info`: (Detailed API or system metadata)

---
Built for production monitoring & troubleshooting.
