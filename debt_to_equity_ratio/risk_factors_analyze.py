# python -m streamlit run risk_factors_analyze.py
import os
# import requests
import openai
import pandas as pd
import streamlit as st
import json

from sec_api import XbrlApi, QueryApi
# Load .env environment variables
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(layout="wide")


class Xbrl:
    # Your API key for the sec-api
    SEC_KEY = os.getenv("SEC")
    xbrlApi = XbrlApi(SEC_KEY)
    queryApi = QueryApi(api_key=SEC_KEY)

    def get_balance_sheet(self, xbrl_json):
        balance_sheet_store = {}

        # Iterate over each US GAAP item in the balance sheet
        for usGaapItem, facts in xbrl_json['BalanceSheets'].items():
            values = []
            indices = []

            # Ensure facts is a list before iterating
            if not isinstance(facts, list):
                print(f"Skipping {usGaapItem} as it's not a list.")
                continue

            for fact in facts:
                # Check if fact is a dictionary
                if not isinstance(fact, dict):
                    print(f"Skipping a fact in {usGaapItem} as it's not a dictionary.")
                    continue

                # Only consider items without segment. Not required for our analysis.
                if 'segment' not in fact and 'period' in fact and 'instant' in fact['period']:
                    # Use 'instant' for index
                    index = fact['period']['instant']
                    
                    # Ensure the 'value' key exists and no index duplicates are created
                    if 'value' in fact and index not in indices:
                        values.append(fact['value'])
                        indices.append(index)
                    else:
                        print(f"No 'value' key for {usGaapItem} on {index}")

            balance_sheet_store[usGaapItem] = pd.Series(values, index=indices, dtype='float64') 

        balance_sheet = pd.DataFrame(balance_sheet_store)
        # Switch columns and rows so that US GAAP items are rows and each column header represents a date
        return balance_sheet.T

    def clean_data(self, balance_sheets_merged, balance_sheet_2023):
        balance_sheets_merged = balance_sheets_merged.sort_index().reset_index()
        balance_sheets_merged = balance_sheets_merged.applymap(lambda x: pd.to_numeric(x, errors= 'ignore'))
        # Aggregate by index and take max
        balance_sheets = balance_sheets_merged.groupby('index').max()

        # Reindex
        balance_sheets = balance_sheets.reindex(balance_sheet_2023.index)

        # Drop columns before 2019 and filter out non-annual data
        cols_to_drop = []
        for col in balance_sheets.columns:
            splitted = col.split('-')
            start = '-'.join(splitted[:3])
            end = '-'.join(splitted[3:])
            start_date = pd.to_datetime(start)
            end_date = pd.to_datetime(end)
            duration = (end_date - start_date).days / 360

            # Drop if duration is less than a year or if the year is before 2019
            if duration < 1 or start_date.year < 2019:
                cols_to_drop.append(col)

        balance_sheets.drop(columns=cols_to_drop, inplace=True)

        # Convert to readable format
        balance_sheets = balance_sheets.apply(lambda row: pd.to_numeric(row, errors='coerce', downcast='integer').astype(str), axis=1)

        # Sort columns
        balance_sheets = balance_sheets[sorted(balance_sheets.columns)]
        return balance_sheets

    def query_tick_filings(self, ticker, date_start, date_end):
        query_srt = f"ticker:{ticker} AND filedAt:[{date_start} TO {date_end}] AND formType:\"10-K\""
        query = {
            "query": { "query_string": { 
                "query": query_srt,
                "time_zone": "America/New_York"
            } },
            "from": "0",
            "size": "10",
            "sort": [{ "filedAt": { "order": "desc" } }]
            }

        # # response is a dict with multiple keys. The most important one is "filings".
        # # response["filings"] is a list and includes all filings returned by the Query API.
        response = self.queryApi.get_filings(query)
        json_filings = json.loads(json.dumps(response["filings"][0], indent=2))
        return json_filings
    
    def get_balance_sheet_from_api(self, json_filings):
        document_format_files = json_filings.get('documentFormatFiles')
        documents_df = pd.DataFrame.from_dict(document_format_files)
        # filter to use only 10-K documents
        doc_10_k_urls = documents_df.loc[documents_df["description"] == "10-K", "documentUrl"].values
        balance_sheets = pd.DataFrame()
        balance_sheet_json = None
        # Read each document and concat the reult to the balance sheet dataFrame
        print(doc_10_k_urls)
        for document_url in doc_10_k_urls:
            xbrl_json = self.xbrlApi.xbrl_to_json(htm_url=document_url)
            balance_sheet_json = self.get_balance_sheet(xbrl_json)
            balance_sheets = pd.concat([balance_sheets, balance_sheet_json], axis=0, sort=False)
        balance_sheets = self.clean_data(balance_sheets, balance_sheet_json)
        return balance_sheets


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
date_start = st.sidebar.date_input("Date start:", value=None)
date_end = st.sidebar.date_input("Date end:", value=None)

if st.sidebar.button("Balance Sheet"):
    try:
        if not date_start or not date_end or not ticker_search:
            st.sidebar.error('Please, fill in all fields.')
        else:
            # Query for the documents
            # json_filings = None
            json_filings = Xbrl().query_tick_filings(ticker_search, date_start, date_end)
            company_name = json_filings.get('companyName')
            balance_sheets = Xbrl().get_balance_sheet_from_api(json_filings)
            st.write(f"""### Balance Sheets of {company_name}""")
            st.write(f"""### from {date_start} to {date_end}""")
            st.dataframe(balance_sheets)
            # st.dataframe(balance_sheet_url)

            st.write("""### Analysis""")
            balance_sheets_analysis = Gpt.analyze_balance_sheet_with_gpt(balance_sheets)
            st.write(f"""{balance_sheets_analysis}""")
    except Exception as err:
        st.write(err)