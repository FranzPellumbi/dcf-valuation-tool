📊 DCF Valuation Tool
A full-stack equity research platform built in Python that replicates institutional-grade valuation workflows. Pulls live financial data, runs discounted cash flow models, generates AI-powered equity research reports, and screens multiple stocks simultaneously — all in a professional dark terminal UI.


🚀 Features
Core Valuation
Full 3-Statement DCF Model — Revenue → EBIT → NOPAT + D&A − CapEx − ΔNWC = Unlevered FCF
Dual Terminal Value Methods — Gordon Growth Model (perpetuity) and Exit Multiple (EV/EBITDA) shown side by side with midpoint
Bull / Base / Bear Scenario Modeling — three independent DCF runs with varying margin, WACC, and growth assumptions
Institutional WACC — built from live 10-year US Treasury rate, actual cost of debt from financials, and effective tax rate from income statement (not hardcoded)
Monte Carlo Simulation — 1,000 runs with probability distribution, percentile breakdown, and probability of overvaluation
Sensitivity Analysis Heatmap — WACC vs terminal growth rate, color-coded
Football Field Chart — valuation range across all methods vs current price
Market Data & Financials
Live financial statement pulls — income statement, cash flow, balance sheet
Historical FCF calculation and projection
Historical margin, CapEx, D&A, and NWC metrics extracted automatically
Real-time stock prices with live market ticker bar (SPY, QQQ, AAPL, NVDA, TSLA, and more)
Comparable Companies Analysis
Auto-detected peer groups by ticker
Live EV/EBITDA, P/E, and P/FCF multiples for 5-6 peers
Implied share price derived from each multiple
Financial Ratios Dashboard
Profitability — Gross Margin, Operating Margin, Net Margin, ROE, ROA
Liquidity & Leverage — Current Ratio, Quick Ratio, Debt/Equity, Interest Coverage
Valuation Multiples — P/E, Forward P/E, P/B, EV/EBITDA, EV/Revenue
Growth — Revenue Growth YoY, Earnings Growth YoY
Analyst & Market Intelligence
Wall Street consensus price targets — mean, median, high, low
Analyst ratings breakdown with stacked bar chart
Insider trading tracker with buy/sell summary and sentiment score
Forward earnings estimates — EPS, revenue, and EPS history vs consensus
AI-Powered Features
AI Equity Research Report — powered by LLaMA 3.3 70B via Groq API. Generates a full sell-side style report with Executive Summary, Investment Thesis, Financial Analysis, Valuation, Risk Factors, and Buy/Hold/Sell recommendation with price target
News Sentiment Analysis — pulls recent headlines, analyzes sentiment via AI, returns Bullish/Bearish/Neutral score with key themes
Portfolio Screener
Input multiple tickers and screen simultaneously
Runs full DCF on each stock automatically
Ranks all stocks from most undervalued to most overvalued
Color-coded results table with downloadable CSV export
Dividend Discount Model (DDM)
Gordon Growth Model for dividend-paying stocks
Auto-detects dividend payers, shows N/A for non-dividend stocks
Export & Reporting
PDF Report — one-page summary with key metrics, assumptions, and FCF projections
Excel Model — 5 professionally formatted tabs (Summary, DCF Model, Historical FCF, Comps, Monte Carlo) with IB-standard color coding
AI Research Report — downloadable as text file
Screener Results — downloadable as CSV

🛠 Tech Stack
Category
Tools
Language
Python 3.12
UI Framework
Streamlit
Data
yfinance, pandas, NumPy
Visualization
Plotly, Matplotlib
AI / LLM
Groq API (LLaMA 3.3 70B)
Statistics
SciPy
Export
fpdf2, openpyxl
Environment
python-dotenv


📁 Project Structure
dcf_tool/
├── app.py                 # Main Streamlit application
├── dcf.py                 # Core DCF logic, WACC, FCF projection
├── monte_carlo.py         # Monte Carlo simulation
├── comps.py               # Comparable companies analysis
├── scenarios.py           # Bull/Base/Bear scenario modeling
├── screener.py            # Multi-stock portfolio screener
├── football_field.py      # Football field chart
├── ratios.py              # Financial ratios dashboard
├── analyst.py             # Analyst price targets and ratings
├── insider.py             # Insider trading tracker
├── earnings.py            # Earnings estimates
├── ddm.py                 # Dividend Discount Model
├── ai_report.py           # AI equity research report generator
├── ticker.py              # Live market ticker bar
├── report.py              # PDF report generation
├── excel_export.py        # Excel model export
├── .env                   # API keys (not committed)
├── .gitignore
└── README.md


⚙️ Setup & Installation
1. Clone the repository
git clone https://github.com/yourusername/dcf-tool.git
cd dcf-tool

2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

3. Install dependencies
pip install streamlit yfinance pandas numpy plotly scipy fpdf2 openpyxl groq python-dotenv matplotlib

4. Set up your API key
Create a .env file in the root directory:
GROQ_API_KEY=your-groq-api-key-here

Get a free Groq API key at console.groq.com
5. Run the app
python -m streamlit run app.py


📊 How to Use
Enter a ticker symbol in the sidebar (e.g. AAPL, MSFT, JPM)
Adjust DCF assumptions — FCF growth rate, terminal growth rate, exit multiple
Click Run Analysis
Scroll through the full valuation dashboard
Use the Portfolio Screener to compare multiple stocks
Click Generate AI Report for a full sell-side research report
Download PDF or Excel exports

⚠️ Disclaimer
This tool is for educational purposes only. All valuations are model-based estimates and should not be used as financial advice. Always conduct your own research before making investment decisions.

👤 Author
Built by Franz — Economics & Financial Management student at Wilfrid Laurier University, targeting Investment Banking.
Connect on LinkedIn 
