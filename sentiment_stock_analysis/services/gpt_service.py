import os
import logging
import openai
# Load .env environment variables
from dotenv import load_dotenv
load_dotenv()


class Gpt:
    # Configure OpenAI library to use your API key
    GPT_KEY = os.environ.get("GPT")
    openai.api_key = GPT_KEY

    def analyze_balance_sheet(self, df):
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
            sentiment_analysis = response.choices[0].text.strip()
            return sentiment_analysis
        except Exception as e:
            logging.error(str(e))
            raise Exception(str(e))

    def perform_sentiment_analysis(self, title):
        # Perform sentiment analysis with OpenAI
        sentiment_analysis = None
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
            logging.error("Sentiment analysis error: " + str(e))
            sentiment_analysis = "Sentiment analysis error: " + str(e)
        return sentiment_analysis

    def read_news_articles(self, news_articles, ticker_symbol, rate_limit):
        # Initialize variables for rate limiting
        api_requests = 0
        # Create a list to store data
        data_list = []
        # Extract data and add it to the list
        print(news_articles)
        for article in news_articles:
            title = article.get("title", "No Title")

            # Implement rate limiting
            api_requests += 1
            if api_requests >= rate_limit:
                break

            # Perform sentiment analysis with OpenAI
            sentiment_analysis = self.perform_sentiment_analysis(title)

            # Add data to the list
            data_list.append({
                "Date": article.get("published_utc", "Unknown Date"),
                "Stock Ticker": ticker_symbol,
                "Title": title,
                "Sentiment": sentiment_analysis
            })
        return data_list

    def analyze_income_statement_with_gpt(self, df):
        try:
            # Convert DataFrame to a string representation for sending to GPT
            income_statement_str = df.to_string()

            prompt_text = f"Please analyze the following income statement data for the last few years:\n\n{income_statement_str}\n\nProvide insights on the revenue, expenses, and net income trends, evaluate profit margins and the operational efficiency of the company in 750 words or less."

            # Make API call to OpenAI
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt_text,
                max_tokens=1000
            )

            # return GPT's analysis
            return response.choices[0].text.strip()
        except Exception as e:
            logging.error(str(e))
            raise Exception(str(e))
        
    def analyze_cash_flows_statement_with_gpt(self, df):
        try:
            # Convert DataFrame to a string representation for sending to GPT
            cash_flows_str = df.to_string()

            prompt_text = f"Please analyze the following cash flows statement data for the last few years:\n\n{cash_flows_str}\n\nProvide insights on the operating, investing, and financing cash flows. Highlight any major changes or trends in cash positions and evaluate the company's ability to generate positive cash flow in 750 words or less."

            # Make API call to OpenAI
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt_text,
                max_tokens=1000
            )

            # Return GPT's analysis
            return response.choices[0].text.strip()
        except Exception as e:
            logging.error(str(e))
            raise Exception(str(e))
        
    def analyze_ratios_with_openai(self, ticker, ratio_df):
        try:
            # Constructing a prompt for the OpenAI API
            prompt = f"""
                        Analyze the financial metrics for the company with ticker symbol {ticker}:

                        - P/E Ratio (Price-to-Earnings Ratio) for {ticker}: {ratio_df["metric"]['P/E Ratio']}
                        Average P/E Ratio among peers: {ratio_df["Average Metrics Among Peers"]['P/E Ratio']}

                        - P/B Ratio (Price-to-Book Ratio) for {ticker}: {ratio_df["metric"]['P/B Ratio']}
                        Average P/B Ratio among peers: {ratio_df["Average Metrics Among Peers"]['P/B Ratio']}

                        - P/S Ratio (Price-to-Sales Ratio) for {ticker}: {ratio_df["metric"]['P/S Ratio']}
                        Average P/S Ratio among peers: {ratio_df["Average Metrics Among Peers"]['P/S Ratio']}

                        - Dividend Yield for {ticker}: {ratio_df["metric"]['Dividend Yield']}
                        Average Dividend Yield among peers: {ratio_df["Average Metrics Among Peers"]['Dividend Yield']}

                        - ROE (Return on Equity) for {ticker}: {ratio_df["metric"]['ROE']}
                        Average ROE among peers: {ratio_df["Average Metrics Among Peers"]['ROE']}

                        - ROA (Return on Assets) for {ticker}: {ratio_df["metric"]['ROA']}
                        Average ROA among peers: {ratio_df["Average Metrics Among Peers"]['ROA']}

                        - Debt-to-Equity Ratio for {ticker}: {ratio_df["metric"]['Debt-to-Equity Ratio']}
                        Average Debt-to-Equity Ratio among peers: {ratio_df["Average Metrics Among Peers"]['Debt-to-Equity Ratio']}

                        - Current Ratio for {ticker}: {ratio_df["metric"]['Current Ratio']}
                        Average Current Ratio among peers: {ratio_df["Average Metrics Among Peers"]['Current Ratio']}

                        - Quick Ratio for {ticker}: {ratio_df["metric"]['Quick Ratio']}
                        Average Quick Ratio among peers: {ratio_df["Average Metrics Among Peers"]['Quick Ratio']}

                        - Operating Margin for {ticker}: {ratio_df["metric"]['Operating Margin']}
                        Average Operating Margin among peers: {ratio_df["Average Metrics Among Peers"]['Operating Margin']}

                        - Gross Margin for {ticker}: {ratio_df["metric"]['Gross Margin']}
                        Average Gross Margin among peers: {ratio_df["Average Metrics Among Peers"]['Gross Margin']}

                        - Price-to-Cash Flow for {ticker}: {ratio_df["metric"]['Price-to-Cash Flow']}
                        Average Price-to-Cash Flow among peers: {ratio_df["Average Metrics Among Peers"]['Price-to-Cash Flow']}

                    Considering the above data points and understanding the importance of these metrics in evaluating a company's financial health and performance:

                1. How does the company stand in terms of profitability, liquidity, and solvency compared to its peers?
                2. Are there any alarming disparities or noteworthy strengths in any specific metrics?
                3. What might these metrics indicate about the company's operational efficiency, financial strategies, or market positioning?
                4. Are there potential opportunities or risks that these metrics highlight?

                Please provide a comprehensive analysis of the company's financial standing compared to its peers.

                    """

            # Querying the OpenAI API
            response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=400)
            analysis = response.choices[0].text.strip()

            return analysis
        except Exception as e:
            logging.error(str(e))
            raise Exception(str(e))