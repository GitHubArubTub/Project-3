import os
import logging
import pandas as pd
import requests
import torch

from simpletransformers.classification import ClassificationModel
from pathlib import Path
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
        
    def make_prediction_from_articles(self, articles):
        headlines = [article['title'] for article in articles]
        # Preprocess headlines
        headlines = [headline.replace(r'\n', ' ') for headline in headlines]

        # Load trained BERT model
        model_path = Path('Resources')

        # model_path = "../fin new NLP/Resources"
        model = ClassificationModel('bert', model_path, args={}, use_cuda=torch.cuda.is_available())

        # Predict sentiments of headlines
        predictions, _ = model.predict(headlines)

        # Convert numeric predictions to string labels
        label_map = {0: 'Positive', 1: 'Negative', 2: 'Neutral'}
        predicted_labels = [label_map[pred] for pred in predictions]

        # Create a DataFrame to display headlines and their predicted sentiments
        df_results = pd.DataFrame({
            'Headline': headlines,
            'Predicted Sentiment': predicted_labels
        })
        return df_results
