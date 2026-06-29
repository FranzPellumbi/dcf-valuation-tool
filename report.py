from fpdf import FPDF
from datetime import datetime

class DCFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "DCF Valuation Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, f"Generated: {datetime.today().strftime('%B %d, %Y')}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, "For educational purposes only. Not financial advice.", align="C")

def generate_report(ticker, current_price, intrinsic_value, wacc, growth_rate, terminal_growth, fcf, projected_fcf):
    pdf = DCFReport()
    pdf.add_page()

    # Company overview
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, f"Company: {ticker}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Key metrics
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Key Metrics", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Current Price:       ${current_price:,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Intrinsic Value:     ${intrinsic_value:,.2f}", new_x="LMARGIN", new_y="NEXT")
    upside = ((intrinsic_value - current_price) / current_price * 100)
    pdf.cell(0, 7, f"Upside/Downside:     {upside:,.2f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Assumptions
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "DCF Assumptions", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"WACC:                {wacc*100:.2f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"FCF Growth Rate:     {growth_rate*100:.1f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Terminal Growth:     {terminal_growth*100:.1f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Historical FCF
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Historical Free Cash Flow", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for date, value in fcf.items():
        pdf.cell(0, 7, f"{str(date)[:10]}:   ${value/1e9:,.2f}B", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Projected FCF
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Projected Free Cash Flow", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for i, value in enumerate(projected_fcf):
        pdf.cell(0, 7, f"Year {i+1}:   ${value/1e9:,.2f}B", new_x="LMARGIN", new_y="NEXT")

    # Save
    filename = f"{ticker}_DCF_Report.pdf"
    pdf.output(filename)
    return filename