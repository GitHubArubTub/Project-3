# Project-3

# Stock Analysis with OpenAI and BERT Machine Learning

This project leverages AI, specifically the OpenAI API and BERT Machine Learning, to perform stock analysis. It retrieves balance sheet information, extracts relevant fundamental data, and pulls news articles from the web and it employs two methods to determine the sentiment (positive or negative) of the news.

## Installation

1. **Clone the Repository**: 
git clone https://github.com/GitHubArubTub/Project-3.git


2. **Install Dependencies**:
- You need to manually install the necessary libraries. Please refer to the list of required libraries below.

## Usage

1. **Run Streamlit**:
To use this application, you must first open Streamlit, which is a Python library for creating web apps. You can run it using the following command:

streamlit run main.py

2. **Input Stock Ticker**:
Once the interface is running, you'll see a text field. Enter the stock ticker you want to analyze.

3. **Execute Analysis**:
After entering the stock ticker, click the "Run" button or perform the necessary action to trigger the analysis.

4. **View Results**:
The application will provide you with the results of the stock analysis.

## Required Libraries

streamlit
altair (include on streamlit)
requests
dotenv
pandas
openai

Please make sure to manually install the required libraries before running the application.

## Examples


# Fundemental Anlysis Example 1

Based on the financial metrics provided, it appears that PTON is not as profitable, liquid, or solvent as its peers. In terms of profitability, PTON has an operating margin of -42.75% and a gross margin of 32.98%, both of which are significantly lower than the average operating margin and gross margin of 5.06% and 38.76% among its peers, respectively. This indicates that PTON is not as efficient in its operations as its peers and is not generating as much profit from its sales. In terms of liquidity, PTON has a current ratio and quick ratio of 2.15 and 1.20, respectively, which are both lower than the average current ratio and quick ratio of 1.92 and 0.88 among its peers. This indicates that PTON has less cash and assets on hand to cover its short-term obligations than its peers. In terms of solvency, PTON has a debt-to-equity ratio of 2.63, which is significantly higher than the average debt-to-equity ratio of 0.86 among its peers. This indicates that PTON has a higher amount of debt relative to its equity, which may make it more difficult for the company to repay its debts.

Overall, the financial metrics indicate that PTON is not as profitable, liquid, or solvent as its peers. There are some alarming disparities in the company's profitability, liquidity, and solvency, which could indicate potential risks for the company.


# Fundemental Anlysis Example 2

Based on the income statement data provided, it appears that the company has seen a steady increase in revenues for each of the past few years. From 2018 to 2022, the company’s total revenue has increased by nearly 48%. This increase can be attributed to the company’s strategic focus on diversifying its offerings and expanding its product portfolio. 

Another interesting observation is that the company’s cost of revenue has been decreasing significantly when compared to revenue. This can be attributed to the company’s focus on streamlining its processes and becoming more efficient. In particular, the cost of revenue decreased from 62% of total revenue in 2018 to 57% of total revenue in 2022.  

The company’s gross profit ratio has steadily increased from 38.3% in 2018 to 43.3% in 2022. This indicates that the company has been able to increase its profitability over the past few years despite increasing its total revenues. The company’s operating expenses have also decreased over the past few years. This suggests that the company has been able to find ways to become more efficient and reduce spending on operating expenses. 

The company’s profits (net income) have also increased slightly over the past few years from $59.5 billion in 2018 to $99.8 billion in 2022. This suggests that the company’s strategies have been resulting in higher profits for the company. Additionally, the company’s earnings per share (EPS) has also increased from $3.00 in 2018 to $6.11 in 2022. This demonstrates the profitability of the company to its shareholders.

Overall, it appears that the company has made significant strides in increasing its profitability and operational efficiency. The company has been able to increase its revenue while simultaneously decreasing operating expenses and cost of revenue. This has resulted in the company increasing its gross profit and net income. Additionally, the company has been able to return more value to its shareholders in the form of increasing EPS. It appears that the company’s strategies have been successful in improving the company’s financial performance and overall operational efficiency.
