# Import libraries and dependencies
import numpy as np
import pandas as pd
import yfinance as yf
import datetime
from datetime import datetime, timedelta
import bitmex
import requests
import json
import time

#bitmex api
bitmex_api_key_test = 'kkNwJW4MLdQ-0RIoBz8tflAY' 
bitmex_api_secret_test = 'N7-ROML4N9bd2zGvZ7EvfNfi7OQI2qVoDqRw2OqCWdJDDzgR'
client = bitmex.bitmex(api_key=bitmex_api_key_test, api_secret=bitmex_api_secret_test)

#variables
orderqty = 100
leverage = 1
symbol_bitmex='XBTUSD'
positions = 0

while True:
    dateee = datetime.now() - timedelta(days=5)
    symbol = yf.Ticker('BTC-USD')
    net_historical = symbol.history(start=dateee, end="2030-12-11", interval="1h")
    signals_df = net_historical.drop(columns=['Dividends', 'Stock Splits'])
    

    #strategy
    signals_df['ma_50'] = signals_df['Close'].rolling(window=50).mean()
    signals_df['previous'] = signals_df['Close'].shift(1)
    
    close = int(signals_df['Close'].tail(1))
    ma = int(signals_df['ma_50'].tail(1))
    pre = int(signals_df['previous'].tail(1))
    processed_position = {}
    if((close>ma) and (pre<=ma)):
        #check positions      
        positions = client.Position.Position_get(filter=json.dumps({"symbol": symbol_bitmex})).result()[0][0]
        processed_position["currentQty"] = positions["currentQty"]
        print(processed_position["currentQty"])
        
        while(positions["currentQty"] <= 0):
            positions = client.Position.Position_get(filter=json.dumps({"symbol": symbol_bitmex})).result()[0][0]
            result = client.Quote.Quote_get(symbol=symbol_bitmex).result()
            processed_position["currentQty"] = positions["currentQty"]
            result = client.Quote.Quote_get(symbol=symbol_bitmex, reverse=True, count=1).result()
            execute_price = result[0][0]['bidPrice']
            if(positions["currentQty"]<=0):
                order = client.Order.Order_new(symbol=symbol_bitmex, orderQty=orderqty, price=execute_price, side='Buy').result()
            print('price_buy:', order[0]['price'])
            print('bid:',result[0][0]['bidPrice'])
            print('sleep 30 seconds')
            time.sleep(30)
            client.Order.Order_cancelAll().result()
            positions = client.Position.Position_get(filter=json.dumps({"symbol": symbol_bitmex})).result()[0][0]
            print('current positions:',positions["currentQty"])
            
    
    
    if((close<ma) and (pre>=ma)):
        #check positions
        positions = client.Position.Position_get(filter=json.dumps({"symbol": symbol_bitmex})).result()[0][0]
        processed_position["currentQty"] = positions["currentQty"]
        
        while(positions["currentQty"] >= 100):
            positions = client.Position.Position_get(filter=json.dumps({"symbol": symbol_bitmex})).result()[0][0]
            result = client.Quote.Quote_get(symbol=symbol_bitmex).result()
            positions = client.Position.Position_get(filter=json.dumps({"symbol": symbol_bitmex})).result()[0][0]
            processed_position["currentQty"] = positions["currentQty"]
            result = client.Quote.Quote_get(symbol=symbol_bitmex, reverse=True, count=1).result()
            execute_price = result[0][0]['askPrice']
            if(positions["currentQty"]>=100):
                order = client.Order.Order_new(symbol=symbol_bitmex, orderQty=orderqty, price=execute_price, side='Sell').result()
            print('price_sell:', order[0]['price'])
            print('ask:',result[0][0]['askPrice'])
            print('sleep 30 seconds')
            time.sleep(30)
            client.Order.Order_cancelAll().result()
            positions = client.Position.Position_get(filter=json.dumps({"symbol": symbol_bitmex})).result()[0][0]
            print('current positions:',positions["currentQty"]) 
    
    
    signals_df.to_csv('btcusd.csv')
    print('sleep 1 hour')
    time.sleep(3600)