import os
import logging
import requests
# Load .env environment variables
from dotenv import load_dotenv
load_dotenv()


class Polygon:
    # ed7eRBk0FDeIor5XgFCSyocd28VQKzPf
    POLYGON = os.getenv("POLYGON")

    def get_articles_from_api(self, ticker_symbol, news_limit):
        # Define the API endpoint for Polygon.io
        polygon_endpoint = f"https://api.polygon.io/v2/reference/news?ticker={ticker_symbol}&limit={news_limit}&apiKey={self.POLYGON}"
        # Make the API request to Polygon.io
        logging.info("Make the API request to Polygon.io")
        response = requests.get(polygon_endpoint)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            news_articles = data.get("results", [])
            return news_articles
        else:
            raise Exception(f"{response.status_code}: Error consulting Polygon api")
