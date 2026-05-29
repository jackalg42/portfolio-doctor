import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Portfolio Doctor", layout="wide")

st.title("Portfolio Doctor")
st.write("Analyze your portfolio concentration, risk, and allocation.")
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
    "Ticker": ["SPY", "QQQ", "NVDA", "MSFT"],
    "Amount": [5000, 3000, 1000, 1000]
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
    holdings["Weight"] = holdings["Amount"] / total_value

    st.subheader("Portfolio Allocation")

    col1, col2, col3 = st.columns(3)

    top_weight = holdings["Weight"].max()
    num_holdings = len(holdings)
    stock_like = holdings[~holdings["Ticker"].isin(["SPY", "VOO", "VTI", "QQQ", "SCHD"])]

    concentration_score = min(100, round(top_weight * 100 + max(0, 10 - num_holdings) * 5))

    col1.metric("Total Portfolio", f"${total_value:,.0f}")
    col2.metric("Number of Holdings", num_holdings)
    col3.metric("Concentration Risk", f"{concentration_score}/100")

    fig = px.pie(
        holdings,
        names="Ticker",
        values="Amount",
        title="Portfolio Weights"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        holdings[["Ticker", "Amount", "Weight"]].assign(
            Weight=lambda x: (x["Weight"] * 100).round(2)
        ),
        use_container_width=True
    )

    st.subheader("Risk Diagnosis")

    diagnosis = []

    if top_weight > 0.25:
        diagnosis.append("Your portfolio is concentrated in one holding above 25%.")
    if num_holdings < 5:
        diagnosis.append("Your portfolio has relatively few holdings, which may increase single-name risk.")
    if risk_tolerance == "Low" and stock_like["Weight"].sum() > 0.5:
        diagnosis.append("Your stated risk tolerance is low, but your portfolio appears equity-heavy.")
    if age < 35 and risk_tolerance == "High":
        diagnosis.append("Your profile can generally tolerate more growth exposure, but concentration risk still matters.")
    if time_horizon == "0-3 years":
        diagnosis.append("Short time horizons usually require more caution and less volatility.")

    if len(diagnosis) == 0:
        diagnosis.append("Your portfolio appears reasonably balanced based on this simple first-pass analysis.")

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

    fig2 = px.bar(
        target_df,
        x="Category",
        y="Target %",
        title="Suggested Target Allocation"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Doctor's Summary")

    st.write(
        f"Based on your age of {age}, {risk_tolerance.lower()} risk tolerance, "
        f"and {time_horizon} time horizon, your biggest issue appears to be "
        f"{'concentration risk' if concentration_score > 40 else 'maintaining diversification'}."
    )
