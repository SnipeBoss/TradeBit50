# Python_Binance documentation : https://python-binance.readthedocs.io/en/latest/
from binance import Client
# CSV documentation : https://docs.python.org/3/library/csv.html
import csv
# External API key and Secret
from config_key import api_key, api_secret

import datetime
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps

# Import lib to receive bitcoin realtime prices
import json
import requests

def login_required(f):
    """
    Decorate routes to require login. src: http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_realtime_btc():
    """
    This code will return JSON format for realtime data of BTC src: https://www.geeksforgeeks.org/get-real-time-crypto-price-using-python-and-binance-api/
    """
    # defining key/request url 
    key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
  
    # requesting data from url 
    data = requests.get(key)   
    data = data.json() 
    
    return data['price']


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


# The testnet parameter will also be used by any websocket streams when the client is passed to the BinanceSocketManager.
client = Client(api_key, api_secret)

# Fetch klines for date range and interval
candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_5MINUTE)

csv_file = open("./static/1minute.csv", "w", newline="")

candle_stick_writer = csv.writer(csv_file, delimiter=',')

for candle in candles:
    print(candle)
    
    candle_stick_writer.writerow(candle)

# Get Historical Kline/Candlesticks
candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC")