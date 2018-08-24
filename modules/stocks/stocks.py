from .stocks_helper import StocksHelper
import yaml
import requests
import os


class Stocks:

    def __init__(self):
        self.helper = StocksHelper()
        self.key = self.get_credentials()

    def get_credentials(self):
        CREDENTIALS_FILE = "{}/stocks-credentials.yaml".format(
            os.path.abspath(os.path.dirname(__file__))
        )
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE) as cf:
                credentials = yaml.load(cf)
                return credentials['ALPHA_VANTAGE_KEY']
        else:
            return os.environ.get('ALPHA_VANTAGE_KEY')

    def get_ticker_price(self, ticker):
        url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}".format(
            ticker, self.key)
        r = requests.get(url)
        return round(float(r.json()["Global Quote"]["05. price"]), 2)

    def route_command(self, command, say, listen):
        label, ticker = self.helper.parse_command(command)
        if label == "price":
            say("The current price of {} is {} dollars.".format(ticker, self.get_ticker_price(ticker)))
        else:
            return False
        return True
