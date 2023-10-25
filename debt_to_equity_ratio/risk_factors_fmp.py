# python -m streamlit run risk_factors_fmp.py
import os
import requests
import openai
import pandas as pd
import streamlit as st

# Load .env environment variables
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(layout="wide")


class Fmp:
    API_KEY = os.getenv("FMP")
    ticker = "AAPL"

    def get_balance_sheet_data(self, ticker, years=5):
        # Construct the URL
        url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={self.API_KEY}&limit={years}"

        # Fetch the data
        response = requests.get(url)
        data = response.json()

        # Convert the data to a pandas dataframe
        df = pd.DataFrame(data)
        return df

    def clean_data(self, df):
        # drop unneeded rows
        df = df.drop(columns=['cik', 'link', 'finalLink'])
        # Extracting year from the 'date' column
        df['year'] = df['date'].str.split('-').str[0]
        # Setting the 'year' column as the index
        df.set_index('year', inplace=True)
        # Transposing the DataFrame
        df_transposed = df.transpose()
        return df_transposed


class Gpt:
    # Configure OpenAI library to use your API key
    GPT_KEY = os.environ.get("GPT")
    openai.api_key = GPT_KEY

    def analyze_balance_sheet_with_gpt(df):
        # Convert DataFrame to a string representation for sending to GPT
        balance_sheet_str = df.to_string()
        prompt_text = f"Please analyze the following balance sheet data for the last few years:\n\n{balance_sheet_str}\n\nProvide insights on the assets, liabilities, and equity trends, and evaluate if the investing risk has increased in 750 words or less."
        # Make API call to OpenAI
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt_text,
            max_tokens=1000
        )

        # Print GPT's analysis
        return response.choices[0].text.strip()


# #### STREAMLIT
ticker_search = st.sidebar.text_input("Ticker:", value="PTON")
years_search = st.sidebar.number_input("Ticker:", value=5, min_value=1, max_value=5)

if st.sidebar.button("Balance Sheet"):
    try:
        if not years_search or not ticker_search:
            st.sidebar.error('Please, fill in all fields.')
        else:
            balance_sheets = Fmp().get_balance_sheet_data(ticker_search, years_search)
            balance_sheets = Fmp().clean_data(balance_sheets)
            st.write(f"""### Balance Sheets of {ticker_search}""")
            st.dataframe(balance_sheets)
            st.write("""### Analysis""")
            balance_sheets_analysis = Gpt.analyze_balance_sheet_with_gpt(balance_sheets)
            st.write(f"""{balance_sheets_analysis}""")
    except Exception as err:
        st.write(err)