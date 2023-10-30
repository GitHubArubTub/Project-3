import os
import logging
import requests
import pandas as pd
# Load .env environment variables
from dotenv import load_dotenv
load_dotenv()


class Fmp:
    API_KEY = os.getenv("FMP")

    def get_balance_sheet_statement(self, ticker, years=5):
        # Construct the URL
        url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={self.API_KEY}&limit={years}"

        # Fetch the data
        logging.info("Getting Balance Sheets from FMP api")
        response = requests.get(url)
        data = response.json()

        # Convert the data to a pandas dataframe
        df = pd.DataFrame(data)
        return df

    def clean_data(self, df):
        logging.info("Cleanning FMP data")
        # drop unneeded rows
        df = df.drop(columns=['cik', 'link', 'finalLink'])
        # Extracting year from the 'date' column
        df['year'] = df['date'].str.split('-').str[0]
        # Setting the 'year' column as the index
        df.set_index('year', inplace=True)
        # Transposing the DataFrame
        df_transposed = df.transpose()
        return df_transposed
    
    def get_income_statement(self, ticker, years=5):
        # Construct the URL
        url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?apikey={self.API_KEY}&limit={years}"

        # Fetch the data
        response = requests.get(url)
        data = response.json()

        # Convert the data to a pandas dataframe
        df = pd.DataFrame(data)

        # Drop specific columns
        df = df.drop(columns=['cik', 'link', 'finalLink'])

        # Set the 'date' field as index and transpose
        df_transposed = df.set_index('date').T

        return df_transposed
    
    def get_cash_flows_data(self, ticker, years=5):
        # Construct the URL
        url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={self.API_KEY}&limit={years}"

        # Fetch the data
        response = requests.get(url)
        data = response.json()

        # Convert the data to a pandas dataframe
        df = pd.DataFrame(data)

        # Drop specific columns
        df = df.drop(columns=['cik', 'link', 'finalLink'])

        # Set the 'date' field as index and transpose
        df_transposed = df.set_index('date').T

        return df_transposed