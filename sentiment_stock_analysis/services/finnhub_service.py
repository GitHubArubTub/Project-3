import os
import logging
import requests
import pandas as pd
# Load .env environment variables
from dotenv import load_dotenv
load_dotenv()


class Finnhub:
    FINNHUB_API_KEY = os.getenv("FINNHUB")
    BASE_URL = "https://finnhub.io/api/v1/"

    headers = {
        "X-Finnhub-Token": FINNHUB_API_KEY
    }

    def get_ratios_for_ticker(self, ticker):       
        """Fetch various financial metrics for the given ticker."""
        response = requests.get(f"{self.BASE_URL}stock/metric?symbol={ticker}&metric=all", headers=self.headers)
        data = response.json()
        metrics = data.get('metric', {})
        json_dic = {'': ['P/E Ratio',
                         'P/B Ratio',
                         'P/S Ratio', 
                         'Dividend Yield', 
                         'ROE', 
                         'ROA', 
                         'Debt-to-Equity Ratio', 
                         'Current Ratio', 
                         'Quick Ratio', 
                         'Operating Margin', 
                         'Gross Margin', 
                         'Price-to-Cash Flow'], 
                    'metric': [metrics.get('peNormalizedAnnual', None),
                               metrics.get('pbAnnual', None), 
                               metrics.get('psAnnual', None), 
                               metrics.get('dividendYieldIndicatedAnnual', None),
                               metrics.get('roeTTM', None),
                               metrics.get('roaTTM', None),
                               metrics.get('totalDebt/totalEquityAnnual', None),
                               metrics.get('currentRatioAnnual', None),
                               metrics.get('quickRatioAnnual', None),
                               metrics.get('operatingMarginAnnual', None),
                               metrics.get('grossMarginAnnual', None),
                               metrics.get('pcfShareAnnual', None),
                               ]
                    }
        ratio_df = pd.DataFrame(data=json_dic)
        ratio_df = ratio_df.set_index([''])
        return ratio_df

    def get_peer_ratios(self, ticker):
        """Fetch average financial metrics for the peers of the given ticker."""
        response = requests.get(f"{self.BASE_URL}stock/peers?symbol={ticker}", headers=self.headers)
        peers = response.json()
        peers_df = pd.DataFrame()
        for peer in peers:
            try:
                ratio_df = self.get_ratios_for_ticker(peer)
                ratio_df = ratio_df.rename(columns={"metric": f"{peer}"}, errors="raise").transpose()
                peers_df = pd.concat([peers_df, ratio_df])
            except Exception as e:
                logging.error(str(e))
        return peers_df
    