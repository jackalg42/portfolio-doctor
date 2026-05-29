import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Portfolio Doctor", layout="wide")

st.title("Portfolio Doctor")
st.write("Analyze portfolio concentration, sector exposure, diversification, risk, and target allocation.")
st.caption("Educational tool only. Not financial advice.")

st.sidebar.header("Investor Profile")

age = st.sidebar.number_input("Age", min_value=18, max_value=100, value=25)
risk_tolerance = st.sidebar.selectbox("Risk tolerance", ["Low", "Medium", "High"])
time_horizon = st.sidebar.selectbox("Time horizon", ["0-3 years", "3-7 years", "7+ years"])

st.header("Enter Your Holdings")

sample = pd.DataFrame({
    "Ticker": ["NVDA", "META", "QQQ", "MSFT", "JPM"],
    "Amount": [3000, 1500, 2500, 2000, 1000]
})

holdings = st.data_editor(sample, num_rows="dynamic", use_container_width=True)

sector_map = {
    "NVDA": "Technology", "MSFT": "Technology", "AAPL": "Technology", "AVGO": "Technology", "AMD": "Technology",
    "META": "Communication Services", "GOOGL": "Communication Services", "GOOG": "Communication Services", "NFLX": "Communication Services",
    "AMZN": "Consumer Discretionary", "TSLA": "Consumer Discretionary",
    "COST": "Consumer Staples", "WMT": "Consumer Staples", "PG": "Consumer Staples",
    "JPM": "Financials", "BAC": "Financials", "V": "Financials", "MA": "Financials",
    "XOM": "Energy", "CVX": "Energy",
    "LLY": "Healthcare", "UNH": "Healthcare", "JNJ": "Healthcare",
    "GE": "Industrials", "CAT": "Industrials",
    "SPY": "Broad Market ETF", "VOO": "Broad Market ETF", "VTI": "Broad Market ETF",
    "QQQ": "Growth ETF", "SCHD": "Dividend ETF",
    "BND": "Bond ETF", "TLT": "Bond ETF", "IEF": "Bond ETF", "SHY": "Bond ETF",
    "GLD": "Commodities", "BTC-USD": "Crypto", "ETH-USD": "Crypto"
}

def letter_grade(score):
    if score >= 90:
        return "A"
    if score >= 85:
        return "A-"
    if score >= 80:
        return "B+"
    if score >= 75:
        return "B"
    if score >= 70:
        return "B-"
    if score >= 65:
        return "C+"
    if score >= 60:
        return "C"
    if score >= 55:
        return "C-"
    return "D"

if st.button("Diagnose Portfolio"):
    holdings["Ticker"] = holdings["Ticker"].str.upper().str.strip()
    holdings["Amount"] = pd.to_numeric(holdings["Amount"], errors="coerce")
    holdings = holdings.dropna()

    total_value = holdings["Amount"].sum()

    if total_value <= 0:
        st.error("Please enter valid portfolio amounts.")
        st.stop()

    holdings["Weight"] = holdings["Amount"] / total_value * 100
    holdings["Sector"] = holdings["Ticker"].map(sector_map).fillna("Unknown")

    num_holdings = len(holdings)
    top_row = holdings.sort_values("Weight", ascending=False).iloc[0]
    top_holding = top_row["Ticker"]
    top_weight = top_row["Weight"]

    sector_df = holdings.groupby("Sector")["Amount"].sum().reset_index()
    sector_df["Weight"] = sector_df["Amount"] / total_value * 100

    tech_growth_weight = sector_df[sector_df["Sector"].isin(["Technology", "Growth ETF"])]["Weight"].sum()
    broad_etf_weight = sector_df[sector_df["Sector"].isin(["Broad Market ETF"])]["Weight"].sum()
    bond_weight = sector_df[sector_df["Sector"].isin(["Bond ETF"])]["Weight"].sum()
    unknown_weight = sector_df[sector_df["Sector"].isin(["Unknown"])]["Weight"].sum()

    # Cluster 1: better scoring system
    concentration_score = max(0, 100 - max(0, top_weight - 15) * 2.5)
    diversification_score = min(100, num_holdings * 12)
    sector_score = max(0, 100 - max(0, tech_growth_weight - 35) * 1.8)
    broad_market_score = min(100, broad_etf_weight * 2)

    risk_match_score = 100

    if risk_tolerance == "Low":
        if tech_growth_weight > 40:
            risk_match_score -= 30
        if bond_weight < 20:
            risk_match_score -= 25
        if time_horizon == "0-3 years":
            risk_match_score -= 20

    elif risk_tolerance == "Medium":
        if tech_growth_weight > 60:
            risk_match_score -= 20
        if broad_etf_weight < 30:
            risk_match_score -= 20

    else:
        if num_holdings < 4:
            risk_match_score -= 15
        if top_weight > 35:
            risk_match_score -= 20

    risk_match_score = max(0, risk_match_score)

    health_score = round(
        concentration_score * 0.25 +
        diversification_score * 0.20 +
        sector_score * 0.25 +
        broad_market_score * 0.15 +
        risk_match_score * 0.15
    )

    grade = letter_grade(health_score)

    if health_score >= 75:
        risk_level = "Lower Risk"
    elif health_score >= 55:
        risk_level = "Moderate Risk"
    else:
        risk_level = "High Risk"

    if top_weight > 25:
        main_issue = "Single-Position Concentration"
    elif tech_growth_weight > 50:
        main_issue = "Tech/Growth Overexposure"
    elif broad_etf_weight < 30:
        main_issue = "Low Broad-Market Exposure"
    elif num_holdings < 5:
        main_issue = "Low Diversification"
    else:
        main_issue = "Balanced"

    st.subheader("Portfolio Doctor Scorecard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio Grade", grade)
    c2.metric("Health Score", f"{health_score}/100")
    c3.metric("Risk Level", risk_level)
    c4.metric("Main Issue", main_issue)

    st.subheader("Subscores")

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Concentration", f"{round(concentration_score)}/100")
    s2.metric("Diversification", f"{round(diversification_score)}/100")
    s3.metric("Sector Balance", f"{round(sector_score)}/100")
    s4.metric("Broad Market", f"{round(broad_market_score)}/100")
    s5.metric("Risk Match", f"{round(risk_match_score)}/100")

    st.subheader("Portfolio Allocation")

    a1, a2, a3 = st.columns(3)
    a1.metric("Total Portfolio", f"${total_value:,.0f}")
    a2.metric("Number of Holdings", num_holdings)
    a3.metric("Top Holding", f"{top_holding}: {top_weight:.1f}%")

    fig_weights = px.pie(holdings, names="Ticker", values="Amount", title="Portfolio Weights")
    st.plotly_chart(fig_weights, use_container_width=True)

    st.dataframe(
        holdings[["Ticker", "Amount", "Weight", "Sector"]].sort_values("Weight", ascending=False),
        use_container_width=True
    )

    st.subheader("Sector Exposure")

    fig_sector = px.pie(sector_df, names="Sector", values="Amount", title="Sector Exposure")
    st.plotly_chart(fig_sector, use_container_width=True)

    st.dataframe(sector_df.sort_values("Weight", ascending=False), use_container_width=True)

    st.subheader("Risk Diagnosis")

    diagnosis = []

    if top_weight > 25:
        diagnosis.append(f"{top_holding} is {top_weight:.1f}% of your portfolio, creating single-position concentration risk.")
    if tech_growth_weight > 50:
        diagnosis.append(f"Technology/growth exposure is {tech_growth_weight:.1f}%, which is high.")
    if broad_etf_weight < 30:
        diagnosis.append(f"Broad-market ETF exposure is only {broad_etf_weight:.1f}%.")
    if num_holdings < 5:
        diagnosis.append("Your portfolio has relatively few holdings.")
    if risk_tolerance == "Low" and time_horizon == "0-3 years":
        diagnosis.append("Your low-risk profile and short time horizon suggest a need for more caution.")
    if unknown_weight > 20:
        diagnosis.append("A meaningful portion of the portfolio has unknown sector classification.")
    if len(diagnosis) == 0:
        diagnosis.append("Your portfolio appears reasonably balanced based on this first-pass analysis.")

    for item in diagnosis:
        st.write("•", item)

    st.subheader("Suggested Target Allocation")

    if risk_tolerance == "Low":
        target = {"Broad Market ETFs": 60, "Bonds/Cash": 30, "Individual Stocks": 10}
    elif risk_tolerance == "Medium":
        target = {"Broad Market ETFs": 70, "Bonds/Cash": 15, "Individual Stocks": 15}
    else:
        target = {"Broad Market ETFs": 75, "Bonds/Cash": 5, "Individual Stocks": 20}

    target_df = pd.DataFrame({
        "Category": list(target.keys()),
        "Target %": list(target.values())
    })

    fig_target = px.bar(target_df, x="Category", y="Target %", title="Suggested Target Allocation")
    st.plotly_chart(fig_target, use_container_width=True)

    st.subheader("Rebalancing Ideas")

    ideas = []

    if broad_etf_weight < target["Broad Market ETFs"]:
        ideas.append("Consider increasing broad-market ETF exposure through funds like VOO, VTI, or SPY.")
    if tech_growth_weight > 50:
        ideas.append("Consider reducing technology/growth concentration or adding healthcare, financials, industrials, or broad-market ETF exposure.")
    if top_weight > 25:
        ideas.append(f"Consider reducing {top_holding} so no single holding dominates the portfolio.")
    if risk_tolerance == "Low" or time_horizon == "0-3 years":
        ideas.append("Consider adding cash, short-term Treasuries, or bond ETFs to reduce volatility.")

    for idea in ideas:
        st.write("•", idea)

    st.subheader("Doctor's Summary")

    st.write(
        f"Your portfolio receives a grade of **{grade}** with a health score of **{health_score}/100**. "
        f"The main issue appears to be **{main_issue.lower()}**. "
        f"Your largest holding is **{top_holding}** at **{top_weight:.1f}%**, and your technology/growth exposure is **{tech_growth_weight:.1f}%**."
    )

    st.caption("This analysis is simplified and should not be treated as personalized financial advice.")
