from fpdf import FPDF
import datetime
import json

class LogReport(FPDF):
    def header(self):
        # Header background
        self.set_fill_color(18, 18, 18)
        self.rect(0, 0, 210, 40, 'F')
        
        # Title
        self.set_font('Arial', 'B', 24)
        self.set_text_color(110, 142, 251)
        self.cell(0, 20, 'Nokia App Log Analyser', 0, 1, 'C')
        
        # Subtitle
        self.set_font('Arial', '', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, f"Advanced Diagnostic Report | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Confidential Diagnostic Data', 0, 0, 'C')

def generate_pdf_report(stats, failures):
    pdf = LogReport()
    pdf.add_page()
    
    # 1. SUMMARY SECTION
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, '1. Executive Summary', 0, 1)
    pdf.set_draw_color(110, 142, 251)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(60, 60, 60)
    summary_text = (
        f"This report provides a comprehensive analysis of the application logs. "
        f"A total of {stats['total']} events were processed. "
        f"The system health is currently rated at {stats['success_rate']}%, "
        f"with {stats['error']} critical failures and {stats['warn']} warnings detected."
    )
    pdf.multi_cell(0, 8, summary_text)
    pdf.ln(5)
    
    # KPI Grid in PDF
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(45, 15, 'Total Events', 1, 0, 'C', 1)
    pdf.cell(45, 15, 'Health %', 1, 0, 'C', 1)
    pdf.cell(45, 15, 'Errors', 1, 0, 'C', 1)
    pdf.cell(45, 15, 'Warnings', 1, 1, 'C', 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(45, 12, str(stats['total']), 1, 0, 'C')
    pdf.cell(45, 12, f"{stats['success_rate']}%", 1, 0, 'C')
    pdf.set_text_color(255, 0, 0)
    pdf.cell(45, 12, str(stats['error']), 1, 0, 'C')
    pdf.set_text_color(255, 165, 0)
    pdf.cell(45, 12, str(stats['warn']), 1, 1, 'C')
    pdf.ln(15)

    # 2. DETAILED FAILURE LOGS
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, '2. Detailed Failure Diagnostics', 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    
    if failures.empty:
        pdf.set_font('Arial', 'I', 12)
        pdf.cell(0, 10, 'No critical API failures detected during this session.', 0, 1)
    else:
        for idx, row in failures.iterrows():
            # Card Header
            pdf.set_fill_color(230, 230, 255)
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(0, 0, 150)
            pdf.cell(0, 10, f" Failure #{idx+1}: {row['api_action']} (Status: {row['api_status']})", 0, 1, 'L', 1)
            
            # Details
            pdf.set_font('Arial', 'B', 9)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(30, 8, 'Method:', 0, 0)
            pdf.set_font('Arial', '', 9)
            pdf.cell(0, 8, str(row['api_method']), 0, 1)
            
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(30, 8, 'Endpoint:', 0, 0)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(0, 8, str(row['api_url']))
            
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(30, 8, 'Timestamp:', 0, 0)
            pdf.set_font('Arial', '', 9)
            pdf.cell(0, 8, str(row['timestamp']), 0, 1)
            
            # Error Payload
            pdf.set_fill_color(250, 250, 250)
            pdf.set_font('Courier', 'B', 8)
            pdf.set_text_color(150, 0, 0)
            pdf.cell(0, 8, ' Error Payload / Stack Trace:', 0, 1, 'L', 1)
            
            pdf.set_font('Courier', '', 7)
            # Try to format JSON if possible, else raw
            try:
                e_payload = json.dumps(json.loads(row['api_error'].replace("'", '"')), indent=2)
            except:
                e_payload = str(row['api_error'])
            
            pdf.multi_cell(0, 5, e_payload[:1000] + ('...' if len(e_payload) > 1000 else ''))
            pdf.ln(10)
            
            # Check for page overflow
            if pdf.get_y() > 250:
                pdf.add_page()

    return pdf.output(dest='S').encode('latin-1', 'ignore')
