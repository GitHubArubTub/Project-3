# pip install -r requirements.txt
# python -m streamlit run index.py
import altair as alt
import pandas as pd
import streamlit as st
import logging

from services.fmp_service import Fmp
from services.gpt_service import Gpt
from services.finnhub_service import Finnhub
from services.polygon_service import Polygon

logging.basicConfig(level=logging.INFO)
st.set_page_config(layout="wide")


def button_sentiment_analisys(ticker_search, news_limit, rate_limit):
    news_articles = Polygon().get_articles_from_api(ticker_search, news_limit)
    if not news_articles:
        raise BaseException("No Articles found.")

    data_list = Gpt().read_news_articles(news_articles, ticker_search, rate_limit)
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
    return filtered_df


# #### STREAMLIT ####
ticker_search = st.sidebar.text_input("Ticker:", value="PTON").upper()
st.sidebar.divider()
years_search = st.sidebar.number_input("Years:", value=5, min_value=1, max_value=5)

if st.sidebar.button("Balance Sheet"):
    try:
        if not years_search or not ticker_search:
            st.sidebar.error('"Ticker" and "Years" are mandatory fields')
        else:
            balance_sheets = Fmp().get_balance_sheet_statement(ticker_search, years_search)
            balance_sheets = Fmp().clean_data(balance_sheets)
            st.write(f"""### Balance Sheets of {ticker_search}""")
            st.dataframe(balance_sheets)
            st.write("""### Analysis""")
            balance_sheets_analysis = Gpt().analyze_balance_sheet(balance_sheets)
            st.write(f"""{balance_sheets_analysis}""")
    except Exception as err:
        st.write(err)

if st.sidebar.button("Income Statement"):
    try:
        if not years_search or not ticker_search:
            st.sidebar.error('"Ticker" and "Years" are mandatory fields')
        else:
            income_statement = Fmp().get_income_statement(ticker_search, years_search)
            # income_statement = Fmp().clean_data(income_statement)
            st.write(f"""### Income Statement of {ticker_search}""")
            st.dataframe(income_statement)
            st.write("""### Analysis""")
            income_statement_analysis = Gpt().analyze_income_statement_with_gpt(income_statement)
            st.write(f"""{income_statement_analysis}""")
    except Exception as err:
        st.write(err)

if st.sidebar.button("Cash Flows"):
    try:
        if not years_search or not ticker_search:
            st.sidebar.error('"Ticker" and "Years" are mandatory fields')
        else:
            income_statement = Fmp().get_cash_flows_data(ticker_search, years_search)
            # income_statement = Fmp().clean_data(income_statement)
            st.write(f"""### Cash Flows of {ticker_search}""")
            st.dataframe(income_statement)
            st.write("""### Analysis""")
            income_statement_analysis = Gpt().analyze_cash_flows_statement_with_gpt(income_statement)
            st.write(f"""{income_statement_analysis}""")
    except Exception as err:
        st.write(err)

st.sidebar.divider()        

if st.sidebar.button("Ratio Comparation"):
    try:
        if not ticker_search:
            st.sidebar.error('"Ticker" is a mandatory field')
        else:
            st.write(f"### {ticker_search} Ratio Comparation")
            ratio_df = Finnhub().get_ratios_for_ticker(ticker_search)
            peers_df = Finnhub().get_peer_ratios(ticker_search)
            avg_metrics = pd.DataFrame(data={"Average Metrics Among Peers": peers_df.mean().transpose()}) 
            ratio_df = pd.concat([ratio_df, avg_metrics], axis=1, join="inner")
            st.dataframe(ratio_df)
            st.write("""### Analysis""")
            analysis_result = Gpt().analyze_ratios_with_openai(ticker_search, ratio_df)
            st.write(analysis_result)
    except Exception as err:
        st.write(err)

st.sidebar.divider()

rate_limit = st.sidebar.number_input("Rate Limit:", value=3, min_value=1, max_value=30)
news_limit = st.sidebar.number_input("News Limit:", value=10, min_value=1, max_value=30)
if st.sidebar.button("Sentiment analysis"):
    try:
        if not rate_limit or not ticker_search:
            st.sidebar.error('"Ticker", "News Limit" and "Rate Limit" are mandatory fields')
        else:
            st.write(f"### {ticker_search} Sentiment analysis")
            sentiment_df = button_sentiment_analisys(ticker_search, news_limit, rate_limit)
            st.dataframe(sentiment_df)
            # Calculate the total number of each sentiment category
            sentiment_counts = sentiment_df['Sentiment'].value_counts()
            # Draw the chart
            if sentiment_counts.size > 0:
                data = pd.DataFrame({
                    'Positive': sentiment_df.loc[sentiment_df['Sentiment'] == "Positive"].value_counts(),
                    'Negative': sentiment_df.loc[sentiment_df['Sentiment'] == "Negative"].value_counts()
                })
                # Melt the DataFrame to have columns and values
                data_melted = data.melt()
                # Create a color scheme for the columns
                column_color_scheme = {
                    'Positive': 'green',
                    'Negative': 'red'
                }
                chart = alt.Chart(data_melted).mark_bar().encode(
                    x=alt.X('variable:N', title='Sentimental'),
                    y=alt.Y('value:Q', title='Count'),
                    color=alt.Color('variable:N', scale=alt.Scale(domain=list(column_color_scheme.keys()), range=list(column_color_scheme.values())))
                )
                # Add a title to the chart
                chart = chart.properties(title='Total Number of Sentiment Categories')

                st.altair_chart(chart)
    except (Exception, BaseException) as err:
        st.write(err)