# python -m streamlit run de_ratio.py
import os
import requests
import pandas as pd
import streamlit as st
# Load .env environment variables
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(layout="wide")
ALFA_VANTAGE_API_KEY = os.getenv("ALPACA_API_KEY")


# Searsh Symbol
# def search_symbol(keyword):
#     url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keyword}&apikey={ALFA_VANTAGE_API_KEY}'
#     r = requests.get(url)
#     data = r.json()
#     return data


# get balance Sheet
def get_balance_sheet(symbol):
    url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={ALFA_VANTAGE_API_KEY}'
    r = requests.get(url)
    return r.json()


def show_balance_sheet(symbol):
    balance_sheet_data = get_balance_sheet(symbol)
    balance_sheet_df = pd.DataFrame(balance_sheet_data.get("annualReports"))
    balance_sheet_df["debit_equity_ratio"] = balance_sheet_df["totalLiabilities"].astype(float) / balance_sheet_df["totalShareholderEquity"].astype(float)

    st.write(f"""# Symbol: {balance_sheet_data.get('symbol')}""")
    st.write("""## BALANCE SHEET """)
    st.dataframe(balance_sheet_df)


# Use a text_input to get the keywords to filter the dataframe
text_search = st.sidebar.text_input("Search Symbols", value="IBM")

if st.sidebar.button("Balance Sheet"):
    show_balance_sheet(text_search)