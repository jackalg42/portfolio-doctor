import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Portfolio Doctor", layout="wide")

st.title("Portfolio Doctor")
st.write("Analyze portfolio concentration, sector exposure, risk, and allocation.")
st.caption("Educational tool only. Not financial advice.")

st.sidebar.header("Investor Profile")

age = st.sidebar.number_input("Age", min_value=18, max_value=100, value=25)

risk_tolerance = st.sidebar.selectbox(
    "Risk tolerance",
    ["Low", "Medium", "High"]
)

time_horizon = st.sidebar.selectbox(
    "Time horizon",
    ["0-3 years", "3-7 years", "7+ years"]
)

st.header("Enter Your Holdings")

sample = pd.DataFrame({
    "Ticker": ["NVDA", "META", "QQQ", "MSFT", "JPM"],
    "Amount": [3000, 1500, 2500, 2000, 1000]
})

holdings = st.data_editor(
    sample,
    num_rows="dynamic",
    use_container_width=True
)

if st.button("Diagnose Portfolio"):
    holdings["Ticker"] = holdings["Ticker"].str.upper().str.strip()
    holdings["Amount"] = pd.to_numeric(holdings["Amount"], errors="coerce")
    holdings = holdings.dropna()

    total_value = holdings["Amount"].sum()

    if total_value <= 0:
        st.error("Please enter valid portfolio amounts.")
        st.stop()

    holdings["Weight"] = holdings["Amount"] / total_value * 100

    sector_map = {
        "NVDA": "Technology",
        "MSFT": "Technology",
        "AAPL": "Technology",
        "AVGO": "Technology",
        "AMD": "Technology",
        "META": "Communication Services",
        "GOOGL": "Communication Services",
        "GOOG": "Communication Services",
        "NFLX": "Communication Services",
        "AMZN": "Consumer Discretionary",
        "TSLA": "Consumer Discretionary",
        "COST": "Consumer Staples",
        "WMT": "Consumer Staples",
        "JPM": "Financials",
        "BAC": "Financials",
        "V": "Financials",
        "MA": "Financials",
        "XOM": "Energy",
        "CVX": "Energy",
        "LLY": "Healthcare",
        "UNH": "Healthcare",
        "JNJ": "Healthcare",
        "GE": "Industrials",
        "CAT": "Industrials",
        "SPY": "Broad Market ETF",
        "VOO": "Broad Market ETF",
        "VTI": "Broad Market ETF",
        "QQQ": "Growth ETF",
        "SCHD": "Dividend ETF",
        "BND": "Bond ETF",
        "TLT": "Bond ETF",
        "GLD": "Commodities",
        "BTC-USD": "Crypto",
        "ETH-USD": "Crypto"
    }

    holdings["Sector"] = holdings["Ticker"].map(sector_map).fillna("Unknown")

    top_weight = holdings["Weight"].max()
    num_holdings = len(holdings)

    concentration_score = min(
        100,
        round(top_weight + max(0, 10 - num_holdings) * 5)
    )

    st.subheader("Portfolio Allocation")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Portfolio", f"${total_value:,.0f}")
    col2.metric("Number of Holdings", num_holdings)
    col3.metric("Concentration Risk", f"{concentration_score}/100")

    fig_weights = px.pie(
        holdings,
        names="Ticker",
        values="Amount",
        title="Portfolio Weights"
    )

    st.plotly_chart(fig_weights, use_container_width=True)

    st.dataframe(
        holdings[["Ticker", "Amount", "Weight", "Sector"]].sort_values(
            "Weight",
            ascending=False
        ),
        use_container_width=True
    )

    st.subheader("Sector Exposure")

    sector_df = (
        holdings
        .groupby("Sector")["Amount"]
        .sum()
        .reset_index()
    )

    sector_df["Weight"] = sector_df["Amount"] / total_value * 100

    fig_sector = px.pie(
        sector_df,
        names="Sector",
        values="Amount",
        title="Sector Exposure"
    )

    st.plotly_chart(fig_sector, use_container_width=True)

    st.dataframe(
        sector_df.sort_values("Weight", ascending=False),
        use_container_width=True
    )

    tech_weight = sector_df[
        sector_df["Sector"].isin(["Technology", "Growth ETF"])
    ]["Weight"].sum()

    broad_etf_weight = sector_df[
        sector_df["Sector"].isin(["Broad Market ETF"])
    ]["Weight"].sum()

    bond_cash_weight = sector_df[
        sector_df["Sector"].isin(["Bond ETF"])
    ]["Weight"].sum()

    individual_stock_weight = 100 - broad_etf_weight - bond_cash_weight

    st.subheader("Risk Diagnosis")

    diagnosis = []

    if top_weight > 25:
        diagnosis.append("Your portfolio is concentrated in one holding above 25%.")

    if num_holdings < 5:
        diagnosis.append("Your portfolio has relatively few holdings, which may increase single-name risk.")

    if tech_weight > 50:
        diagnosis.append("Your portfolio has heavy technology/growth exposure above 50%.")

    if broad_etf_weight < 40:
        diagnosis.append("Your portfolio may have limited broad-market diversification.")

    if risk_tolerance == "Low" and individual_stock_weight > 50:
        diagnosis.append("Your stated risk tolerance is low, but your portfolio appears equity-heavy.")

    if time_horizon == "0-3 years":
        diagnosis.append("Short time horizons usually require more caution and less volatility.")

    if age < 35 and risk_tolerance == "High":
        diagnosis.append("Your profile can generally tolerate more growth exposure, but concentration risk still matters.")

    if len(diagnosis) == 0:
        diagnosis.append("Your portfolio appears reasonably balanced based on this first-pass analysis.")

    for item in diagnosis:
        st.write("•", item)

    st.subheader("Suggested Target Allocation")

    if risk_tolerance == "Low":
        target = {
            "Broad Market ETFs": 60,
            "Bonds/Cash": 30,
            "Individual Stocks": 10
        }
    elif risk_tolerance == "Medium":
        target = {
            "Broad Market ETFs": 70,
            "Bonds/Cash": 15,
            "Individual Stocks": 15
        }
    else:
        target = {
            "Broad Market ETFs": 75,
            "Bonds/Cash": 5,
            "Individual Stocks": 20
        }

    target_df = pd.DataFrame({
        "Category": list(target.keys()),
        "Target %": list(target.values())
    })

    fig_target = px.bar(
        target_df,
        x="Category",
        y="Target %",
        title="Suggested Target Allocation"
    )

    st.plotly_chart(fig_target, use_container_width=True)

    st.subheader("Doctor's Summary")

    if concentration_score > 50:
        main_issue = "concentration risk"
    elif tech_weight > 50:
        main_issue = "technology/growth overexposure"
    elif broad_etf_weight < 40:
        main_issue = "limited broad-market diversification"
    else:
        main_issue = "maintaining diversification"

    st.write(
        f"Based on your age of {age}, {risk_tolerance.lower()} risk tolerance, "
        f"and {time_horizon} time horizon, your biggest issue appears to be "
        f"{main_issue}."
    )

    st.write(
        "A more balanced version of this portfolio would likely increase broad-market ETF exposure, "
        "reduce excessive single-stock concentration, and align risk with your time horizon."
    )
