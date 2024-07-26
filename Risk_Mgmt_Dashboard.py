#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 00:10:59 2024

@author: rickyabuki-soh
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from statsmodels.regression.rolling import RollingOLS
from statsmodels.api import add_constant

# Set up the Streamlit app
st.title("Financial Dashboard")

# Portfolio management section
st.sidebar.header("Portfolio Management")

# Portfolio data
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=['Ticker', 'Company Name', 'Shares', 'Purchase Price', 'Purchase Date', 'Sector'])

# Add a new stock to the portfolio
with st.sidebar.form("add_stock"):
    st.write("Add a new stock to the portfolio")
    ticker = st.text_input("Ticker")
    company_name = st.text_input("Company Name")
    shares = st.number_input("Number of Shares", min_value=1)
    purchase_price = st.number_input("Purchase Price", min_value=0.0)
    purchase_date = st.date_input("Purchase Date", value=datetime.today())
    sector = st.selectbox("Sector", ['Technology', 'Healthcare', 'Finance', 'Consumer Discretionary', 'Consumer Staples', 'Energy', 'Utilities', 'Real Estate', 'Industrials', 'Materials'])
    add_button = st.form_submit_button("Add Stock")

if add_button:
    new_stock = pd.DataFrame([[ticker, company_name, shares, purchase_price, purchase_date, sector]],
                             columns=['Ticker', 'Company Name', 'Shares', 'Purchase Price', 'Purchase Date', 'Sector'])
    st.session_state.portfolio = st.session_state.portfolio.append(new_stock, ignore_index=True)

# Remove shares from the portfolio
with st.sidebar.form("remove_stock"):
    st.write("Remove shares from the portfolio")
    ticker_remove = st.text_input("Ticker to Remove")
    shares_remove = st.number_input("Number of Shares to Remove", min_value=1)
    sale_price = st.number_input("Sale Price", min_value=0.0)
    sale_date = st.date_input("Sale Date", value=datetime.today())
    remove_button = st.form_submit_button("Remove Shares")

if remove_button:
    for index, row in st.session_state.portfolio.iterrows():
        if row['Ticker'] == ticker_remove and row['Shares'] >= shares_remove:
            st.session_state.portfolio.at[index, 'Shares'] -= shares_remove
            if st.session_state.portfolio.at[index, 'Shares'] == 0:
                st.session_state.portfolio = st.session_state.portfolio.drop(index)
            break

st.write("Current Portfolio")
st.dataframe(st.session_state.portfolio)

# Portfolio returns visualization
st.sidebar.header("Returns Visualization")
start_date = st.sidebar.date_input("Start Date", value=datetime.today() - pd.DateOffset(years=1))
end_date = st.sidebar.date_input("End Date", value=datetime.today())

# Benchmarks
benchmarks = ['S&P 500', 'Nasdaq', 'Dow Jones', 'TSX']
benchmark_tickers = {'S&P 500': '^GSPC', 'Nasdaq': '^IXIC', 'Dow Jones': '^DJI', 'TSX': '^GSPTSE'}
selected_benchmarks = st.sidebar.multiselect("Select Benchmarks", benchmarks)

# Fetching data
tickers = st.session_state.portfolio['Ticker'].unique().tolist()
data = yf.download(tickers + list(benchmark_tickers.values()), start=start_date, end=end_date)['Adj Close']

# Calculate portfolio returns
portfolio_returns = (data[tickers].pct_change().mean(axis=1)).dropna()
benchmark_returns = data[list(benchmark_tickers.values())].pct_change().dropna()

# Plot portfolio returns
fig = go.Figure()
fig.add_trace(go.Scatter(x=portfolio_returns.index, y=(1 + portfolio_returns).cumprod(), mode='lines', name='Portfolio'))

for benchmark in selected_benchmarks:
    fig.add_trace(go.Scatter(x=benchmark_returns.index, y=(1 + benchmark_returns[benchmark_tickers[benchmark]]).cumprod(), mode='lines', name=benchmark))

fig.update_layout(title="Portfolio Returns", xaxis_title="Date", yaxis_title="Cumulative Return")
st.plotly_chart(fig)

# Sector weight pie chart
sector_weights = st.session_state.portfolio.groupby('Sector').sum()['Shares'] / st.session_state.portfolio['Shares'].sum()
fig = px.pie(names=sector_weights.index, values=sector_weights.values, title='Portfolio Sector Weights')
st.plotly_chart(fig)

# Financial metrics section
st.header("Financial Metrics")

# Placeholder for the metrics
st.write("Calculating financial metrics...")

# Assume some financial metrics calculations here (placeholders)
metrics = {
    "Alpha": 0.05,
    "Beta": 1.1,
    "Tracking Error": 0.02,
    "Sharpe Ratio": 1.5,
    "Sortino Ratio": 2.0,
    "VaR": 0.01,
    "CVaR": 0.015,
    "Standard Deviation": 0.1,
    "Downside Deviation": 0.05,
    "Max Drawdown": 0.2,
    "Information Ratio": 0.5,
    "Treynor's Ratio": 0.7,
    "Jensen's Alpha": 0.03
}

for key, value in metrics.items():
    st.write(f"{key}: {value}")

# Interactive ESG score bar chart
st.header("ESG Scores")

# Placeholder ESG scores
esg_scores = {
    'Technology': {'AAPL': 90, 'MSFT': 85},
    'Healthcare': {'JNJ': 80, 'PFE': 75},
    'Finance': {'JPM': 70, 'BAC': 65}
}

esg_data = []
for sector, companies in esg_scores.items():
    for company, score in companies.items():
        esg_data.append({'Sector': sector, 'Company': company, 'ESG Score': score})

esg_df = pd.DataFrame(esg_data)

# Average ESG score by sector
avg_esg_sector = esg_df.groupby('Sector')['ESG Score'].mean().reset_index()
fig = px.bar(avg_esg_sector, x='Sector', y='ESG Score', title='Average ESG Score by Sector')
st.plotly_chart(fig)

# Display ESG scores by company within sector
selected_sector = st.selectbox("Select Sector to View ESG Scores by Company", avg_esg_sector['Sector'].unique())
sector_companies = esg_df[esg_df['Sector'] == selected_sector]
fig = px.bar(sector_companies, x='Company', y='ESG Score', title=f'ESG Scores in {selected_sector} Sector')
st.plotly_chart(fig)

streamlit run Risk_Mgmt_Dashboard.py






