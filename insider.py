import yfinance as yf
import pandas as pd


def get_insider_trades(ticker):
    stock = yf.Ticker(ticker)
    try:
        insider_df = stock.insider_transactions
        if insider_df is None or insider_df.empty:
            return None


        # Rename columns to match actual yfinance output
        rename_map = {
            "Start Date": "Date",
            "Filer Name": "Name",
            "Filer Relation": "Role",
            "Transaction": "Transaction",
            "Shares": "Shares",
            "Value": "Value ($)"
        }
        insider_df = insider_df.rename(columns=rename_map)


        # Keep only columns that exist
        keep = [c for c in ["Date", "Name", "Role", "Transaction", "Shares", "Value ($)"] if c in insider_df.columns]
        insider_df = insider_df[keep].copy()


        if "Date" in insider_df.columns:
            insider_df["Date"] = pd.to_datetime(insider_df["Date"]).dt.strftime("%Y-%m-%d")


        if "Value ($)" in insider_df.columns:
            insider_df["Value ($)"] = insider_df["Value ($)"].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) and x != 0 else "N/A"
            )


        return insider_df.head(15)
    except:
        return None


def get_insider_summary(ticker):
    stock = yf.Ticker(ticker)
    try:
        insider_df = stock.insider_transactions
        if insider_df is None or insider_df.empty:
            return None


        buys = insider_df[insider_df["Shares"] > 0]["Shares"].sum()
        sells = insider_df[insider_df["Shares"] < 0]["Shares"].abs().sum()
        net = buys - sells


        return {
            "total_buys": int(buys),
            "total_sells": int(sells),
            "net_shares": int(net),
            "sentiment": "Bullish" if net > 0 else "Bearish"
        }
    except:
        return None


