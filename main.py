from binance.client import Client
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()


API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

client = Client(API_KEY, API_SECRET)


def get_minute_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(
        symbol, interval, lookback+' min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def plot_crypto(symbol):
    crypto = get_minute_data(symbol, '1m', '30')
    crypto_data = crypto.Open

    plt.plot(crypto_data)
    plt.title('Crypto - Past 30 Minutes', fontsize=20, pad=2.0)
    get_minute_data('BTCUSDT', '1m', '30')


def trade_strategy(symbol, qty, entried=False):
    df = get_minute_data(symbol, '1m', '30m')
    cumul_return = (df.Open.pct_change() + 1).cumprod() - 1
    if not entried:
        if cumul_return[-1] < -0.002:
            order = client.create_order(
                symbol=symbol, side='BUY', type='MARKET', quantity=qty)
            print(order)
            entried = True
        else:
            print('No Trade has been executed')
    if entried:
        while True:
            df = get_minute_data(symbol, '1m', '30m')
            since_buy = df.loc[df.index > pd.to_datetime(
                order['transactTime'], unit='ms')]
            if len(since_buy) > 0:
                since_buy_return = (
                    since_buy.Open.pct_change() + 1).cumprod() - 1
                if since_buy_return[-1] > 0.0015 or since_buy_return[-1] < -0.0015:
                    order = client.create_order(
                        symbol=symbol, side='SELL', type='MARKET', quantity=qty)
                    print(order)
                    break


def main():
    symbol = input('Enter crypto symbol you want to trade: ')
    quantity = input('Enter quantity you would like to trade: ')
    trade_strategy(symbol.upper(), quantity)


if __name__ == '__main__':
    main()
