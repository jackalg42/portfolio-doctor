import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Portfolio Doctor", layout="wide")

st.title("Portfolio Doctor")
st.write("Analyze portfolio concentration, sector exposure, diversification, risk, and target allocation.")
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

sector_map = {
    "NVDA": "Technology", "MSFT": "Technology", "AAPL": "Technology",
    "AVGO": "Technology", "AMD": "Technology", "ORCL": "Technology",
    "CRM": "Technology", "ADBE": "Technology", "INTC": "Technology",
    "META": "Communication Services", "GOOGL": "Communication Services",
    "GOOG": "Communication Services", "NFLX": "Communication Services",
    "DIS": "Communication Services",
    "AMZN": "Consumer Discretionary", "TSLA": "Consumer Discretionary",
    "HD": "Consumer Discretionary", "MCD": "Consumer Discretionary",
    "COST": "Consumer Staples", "WMT": "Consumer Staples",
    "PG": "Consumer Staples", "KO": "Consumer Staples", "PEP": "Consumer Staples",
    "JPM": "Financials", "BAC": "Financials", "V": "Financials",
    "MA": "Financials", "GS": "Financials", "MS": "Financials",
    "XOM": "Energy", "CVX": "Energy", "OXY": "Energy",
    "LLY": "Healthcare", "UNH": "Healthcare", "JNJ": "Healthcare",
    "PFE": "Healthcare", "MRK": "Healthcare",
    "GE": "Industrials", "CAT": "Industrials", "BA": "Industrials",
    "SPY": "Broad Market ETF", "VOO": "Broad Market ETF", "VTI": "Broad Market ETF",
    "QQQ": "Growth ETF", "SCHD": "Dividend ETF", "DIA": "Broad Market ETF",
    "IWM": "Small Cap ETF", "BND": "Bond ETF", "TLT": "Bond ETF",
    "IEF": "Bond ETF", "SHY": "Bond ETF", "GLD": "Commodities",
    "SLV": "Commodities", "BTC-USD": "Crypto", "ETH-USD": "Crypto"
}

def portfolio_grade(score):
    if score >= 90:
        return "A"
    elif score >= 85:
        return "A-"
    elif score >= 80:
        return "B+"
    elif score >= 75:
        return "B"
    elif score >= 70:
        return "B-"
    elif score >= 65:
        return "C+"
    elif score >= 60:
        return "C"
    elif score >= 55:
        return "C-"
    else:
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
    top_weight = holdings["Weight"].max()
    top_holding = holdings.sort_values("Weight", ascending=False).iloc[0]["Ticker"]

    sector_df = holdings.groupby("Sector")["Amount"].sum().reset_index()
    sector_df["Weight"] = sector_df["Amount"] / total_value * 100

    tech_growth_weight = sector_df[
        sector_df["Sector"].isin(["Technology", "Growth ETF"])
    ]["Weight"].sum()

    broad_etf_weight = sector_df[
        sector_df["Sector"].isin(["Broad Market ETF"])
    ]["Weight"].sum()

    bond_weight = sector_df[
        sector_df["Sector"].isin(["Bond ETF"])
    ]["Weight"].sum()

    unknown_weight = sector_df[
        sector_df["Sector"].isin(["Unknown"])
    ]["Weight"].sum()

    individual_stock_weight = 100 - broad_etf_weight - bond_weight

    concentration_score = min(100, round(top_weight + max(0, 10 - num_holdings) * 5))
    risk_score = 0

    if top_weight > 25:
        risk_score += 20
    if num_holdings < 5:
        risk_score += 15
    if tech_growth_weight > 50:
        risk_score += 20
    if broad_etf_weight < 40:
        risk_score += 15
    if risk_tolerance == "Low" and individual_stock_weight > 50:
        risk_score += 15
    if time_horizon == "0-3 years":
        risk_score += 15
    if unknown_weight > 20:
        risk_score += 10

    risk_score = min(100, risk_score)
    health_score = max(0, 100 - risk_score)
    grade = portfolio_grade(health_score)

    if risk_score >= 70:
        risk_label = "High Risk"
    elif risk_score >= 40:
        risk_label = "Moderate Risk"
    else:
        risk_label = "Lower Risk"

    if concentration_score > 50:
        main_issue = "single-position concentration"
    elif tech_growth_weight > 50:
        main_issue = "technology/growth overexposure"
    elif broad_etf_weight < 40:
        main_issue = "limited broad-market diversification"
    elif time_horizon == "0-3 years":
        main_issue = "short time horizon risk"
    else:
        main_issue = "maintaining diversification"

    st.subheader("Portfolio Doctor Scorecard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio Grade", grade)
    c2.metric("Health Score", f"{health_score}/100")
    c3.metric("Risk Level", risk_label)
    c4.metric("Main Issue", main_issue.title())

    st.subheader("Portfolio Allocation")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Portfolio", f"${total_value:,.0f}")
    col2.metric("Number of Holdings", num_holdings)
    col3.metric("Top Holding", f"{top_holding}: {top_weight:.1f}%")

    fig_weights = px.pie(
        holdings,
        names="Ticker",
        values="Amount",
        title="Portfolio Weights"
    )
    st.plotly_chart(fig_weights, use_container_width=True)

    st.dataframe(
        holdings[["Ticker", "Amount", "Weight", "Sector"]].sort_values("Weight", ascending=False),
        use_container_width=True
    )

    st.subheader("Sector Exposure")

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

    st.subheader("Risk Diagnosis")

    diagnosis = []

    if top_weight > 25:
        diagnosis.append(f"{top_holding} is above 25% of your portfolio, creating single-name concentration risk.")

    if num_holdings < 5:
        diagnosis.append("Your portfolio has relatively few holdings, which may increase single-name risk.")

    if tech_growth_weight > 50:
        diagnosis.append(f"Technology/growth exposure is {tech_growth_weight:.1f}%, which is high.")

    if broad_etf_weight < 40:
        diagnosis.append(f"Broad-market ETF exposure is only {broad_etf_weight:.1f}%, which may limit diversification.")

    if risk_tolerance == "Low" and individual_stock_weight > 50:
        diagnosis.append("Your stated risk tolerance is low, but your portfolio appears equity-heavy.")

    if time_horizon == "0-3 years":
        diagnosis.append("Short time horizons usually require more caution, more liquidity, and less volatility.")

    if unknown_weight > 20:
        diagnosis.append("A meaningful part of your portfolio has unknown sector classification.")

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

    st.subheader("Rebalancing Ideas")

    ideas = []

    if broad_etf_weight < target["Broad Market ETFs"]:
        ideas.append("Consider increasing broad-market ETF exposure through funds like VOO, VTI, or SPY.")

    if tech_growth_weight > 50:
        ideas.append("Consider reducing technology/growth concentration or adding exposure to healthcare, financials, industrials, or broad-market ETFs.")

    if top_weight > 25:
        ideas.append(f"Consider reducing {top_holding} so no single position dominates the portfolio.")

    if risk_tolerance == "Low" or time_horizon == "0-3 years":
        ideas.append("Consider adding cash, short-term Treasuries, or bond ETFs to reduce volatility.")

    if len(ideas) == 0:
        ideas.append("Your allocation does not show major red flags based on the current model.")

    for idea in ideas:
        st.write("•", idea)

    st.subheader("Doctor's Summary")

    st.write(
        f"Your portfolio receives a grade of **{grade}** with a health score of **{health_score}/100**. "
        f"The main issue appears to be **{main_issue}**. "
        f"Your largest holding is **{top_holding}** at **{top_weight:.1f}%**, and your technology/growth exposure is **{tech_growth_weight:.1f}%**."
    )

    st.write(
        "A more balanced version of this portfolio would likely increase broad-market ETF exposure, "
        "reduce excessive single-stock or sector concentration, and better align risk with your stated time horizon."
    )

    st.caption("This analysis is simplified and should not be treated as personalized financial advice.")
