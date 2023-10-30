# python -m streamlit run risk_factors_fmp.py
import os
import requests
import logging
import openai
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load .env environment variables
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(layout="wide")

logging.basicConfig(level=logging.DEBUG)


class Fmp:
    API_KEY = os.getenv("FMP")
    ticker = "AAPL"

    def get_balance_sheet_data(self, ticker, years=5):
        # Construct the URL
        url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={self.API_KEY}&limit={years}"

        # Fetch the data
        logging.info("Getting BAlance Sheets from financialmodelingprep api")
        response = requests.get(url)
        data = response.json()

        # Convert the data to a pandas dataframe
        df = pd.DataFrame(data)
        return df

    def clean_data(self, df):
        logging.info("Cleanning data")
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
        try:
            balance_sheet_str = df.to_string()
            prompt_text = f"Please analyze the following balance sheet data for the last few years:\n\n{balance_sheet_str}\n\nProvide insights on the assets, liabilities, and equity trends, and evaluate if the investing risk has increased in 750 words or less."
            # Make API call to OpenAI
            logging.info("Analyzing balance sheet with gpt")
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt_text,
                max_tokens=1000
            )
        except Exception as e:
            sentiment_analysis = "Sentiment analysis error: " + str(e)
            logging.error(sentiment_analysis)
        # Print GPT's analysis
        return response.choices[0].text.strip()
    
    def perform_sentiment_analysis(title):
        # Perform sentiment analysis with OpenAI
        try:
            logging.info("Processing sentimental analysis")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You will be provided with an article title, and your task is to determine the sentiment"
                    },
                    {
                        "role": "user",
                        "content": title
                    }
                ],
                temperature=0,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            sentiment_analysis = response['choices'][0]['message']['content']
        except Exception as e:
            sentiment_analysis = "Sentiment analysis error: " + str(e)
            logging.error(sentiment_analysis)
        return sentiment_analysis


class Finnhub:
    FINNHUB_API_KEY = os.getenv("FINNHUB")
    BASE_URL = "https://finnhub.io/api/v1/"

    headers = {
        "X-Finnhub-Token": FINNHUB_API_KEY
    }

    def get_ratios_for_ticker(self, ticker):
        """Fetch P/E, P/B, and P/S ratios for the given ticker."""
        response = requests.get(f"{self.BASE_URL}stock/metric?symbol={ticker}&metric=all", headers=self.headers)
        data = response.json()
        
        pe_ratio = data['metric']['peNormalizedAnnual']
        pb_ratio = data['metric']['pbAnnual']
        ps_ratio = data['metric']['psAnnual']
        
        return pe_ratio, pb_ratio, ps_ratio

    def get_peers_of_ticker(self, ticker):
        """Fetch the list of peers for the given ticker."""
        response = requests.get(f"{self.BASE_URL}stock/peers?symbol={ticker}", headers=self.headers)
        peers = response.json()
        return peers

    def get_peer_ratios(self, ticker):
        """Fetch average P/E, P/B, and P/S ratios for the peers of the given ticker."""
        peers = self.get_peers_of_ticker(ticker)
        pe_ratios, pb_ratios, ps_ratios = [], [], []

        for peer in peers:
            try:
                pe, pb, ps = self.get_ratios_for_ticker(peer)
                if pe is not None:
                    pe_ratios.append(pe)
                if pb is not None:
                    pb_ratios.append(pb)
                if ps is not None:
                    ps_ratios.append(ps)
            except Exception:
                pass

        avg_pe = sum(pe_ratios) / len(pe_ratios) if pe_ratios else None
        avg_pb = sum(pb_ratios) / len(pb_ratios) if pb_ratios else None
        avg_ps = sum(ps_ratios) / len(ps_ratios) if ps_ratios else None

        return avg_pe, avg_pb, avg_ps


class Polygon:
    # ed7eRBk0FDeIor5XgFCSyocd28VQKzPf
    POLYGON = os.getenv("POLYGON")

    def get_articles(self, ticker_symbol, news_limit, rate_limit):
        # Set the number of news articles you want to retrieve
        # limit = 10
        # Define the rate limit for API requests per minute
        # rate_limit = 10  # Adjust as needed
        # Initialize variables for rate limiting
        api_requests = 0
        # Create a list to store data
        data_list = []
        # Define the API endpoint for Polygon.io
        polygon_endpoint = f"https://api.polygon.io/v2/reference/news?ticker={ticker_symbol}&limit={news_limit}&apiKey={self.POLYGON}"
        # Make the API request to Polygon.io
        logging.info("Make the API request to Polygon.io")
        response = requests.get(polygon_endpoint)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            news_articles = data.get("results", [])

            # Extract data and add it to the list
            for article in news_articles:
                title = article.get("title", "No Title")

                # Implement rate limiting
                api_requests += 1
                if api_requests >= rate_limit:
                    break

                # Perform sentiment analysis with OpenAI
                sentiment_analysis = Gpt.perform_sentiment_analysis(title)

                # Add data to the list
                data_list.append({
                    "Date": article.get("published_utc", "Unknown Date"),
                    "Stock Ticker": ticker_symbol,
                    "Title": title,
                    "Sentiment": sentiment_analysis
                })
        return data_list

    def filter_analysis(self, data_list):
        # Create a DataFrame from the data list
        df = pd.DataFrame(data_list)
        # Filter the DataFrame to keep only "Positive" and "Negative" sentiments
        filtered_df = df[df['Sentiment'].isin(['Positive', 'Negative'])]
        # Reset the index for the new DataFrame
        filtered_df.reset_index(drop=True, inplace=True)
        # Add a new column 'Sentiment_Label' with 1 for 'Positive' and 0 for 'Negative'
        filtered_df = filtered_df.copy()  # Create a copy to avoid the warning
        filtered_df['Sentiment_Label'] = filtered_df['Sentiment'].apply(lambda x: 1 if x == 'Positive' else 0)
        # Sort the DataFrame by the "Date" column in ascending order
        filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
        filtered_df = filtered_df.sort_values(by='Date')
        # Reset the index for the sorted DataFrame
        filtered_df.reset_index(drop=True, inplace=True)
        # Print the sorted DataFrame
        return filtered_df
    
    def sentiment_analysis(self, ticker_symbol, news_limit, rate_limit):
        data_list = self.get_articles(ticker_symbol, news_limit, rate_limit)
        filtered_df = self.filter_analysis(data_list)
        return filtered_df


# #### STREAMLIT ####
ticker_search = st.sidebar.text_input("Ticker:", value="PTON").upper()
years_search = st.sidebar.number_input("Years:", value=5, min_value=1, max_value=5)

if st.sidebar.button("Balance Sheet"):
    try:
        if not years_search or not ticker_search:
            st.sidebar.error('"Ticker" and "Years" are mandatory fields')
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

if st.sidebar.button("Ratio Comparation"):
    try:
        if not ticker_search:
            st.sidebar.error('"Ticker" is a mandatory field')
        else:
            # Fetch ratios for the given ticker
            pe, pb, ps = Finnhub().get_ratios_for_ticker(ticker_search)
            # Fetch average ratios for the peers of the given ticker
            avg_pe, avg_pb, avg_ps = Finnhub().get_peer_ratios(ticker_search)
            data = {"Ratios:": [pe, pb, ps], "Average Ratios Among Peers:": [avg_pe, avg_pb, avg_ps]}
            ratios_df = pd.DataFrame(data=data, index=["P/E Ratio:", "P/B Ratio:", "P/S Ratio:"])

            st.write(f"### {ticker_search} Ratio Comparation")
            st.dataframe(ratios_df)

    except Exception as err:
        st.write(err)

rate_limit = st.sidebar.number_input("Rate Limit:", value=10, min_value=1, max_value=30)
news_limit = st.sidebar.number_input("News Limit:", value=10, min_value=1, max_value=30)
if st.sidebar.button("Sentiment analysis"):
    try:
        if not rate_limit or not ticker_search:
            st.sidebar.error('"Ticker", "News Limit" and "Rate Limit" are mandatory fields')
        else:
            filtered_df = Polygon().sentiment_analysis(ticker_search, news_limit, rate_limit)
            st.write(f"### {ticker_search} Sentiment analysis")
            st.dataframe(filtered_df)

            # Calculate the total number of each sentiment category
            sentiment_counts = filtered_df['Sentiment'].value_counts()

            if sentiment_counts.size > 0:
                # Plot the bar chart
                plt.figure(figsize=(1.6, 1.2))
                sentiment_counts.plot(kind='bar', color=['g', 'r'])
                plt.xlabel('Sentiment')
                plt.ylabel('Count')
                plt.title('Total Number of Sentiment Categories')
                plt.xticks(rotation=0)  # Keep the x-axis labels horizontal
                st.pyplot(plt, use_container_width=False)
    except Exception as err:
        st.write(err)