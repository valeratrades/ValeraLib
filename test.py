import threading, os, requests, pandas as pd, numpy as np
from datetime import datetime, timedelta

from DataScience import plotly_closes
from Binance import Binance
Binance = Binance()
from Valera import dbg

hours_selected = 24
timeframe = 5
script_dir = os.path.dirname(os.path.abspath(__file__))

def get_historical_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={timeframe}m"

    time_ago = datetime.now() - timedelta(hours=hours_selected)
    time_ago_ms = int(time_ago.timestamp() * 1000)
    url += f"&startTime={time_ago_ms}"

    raw_data = requests.get(url).json()
    df = pd.DataFrame(raw_data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                         'quote_asset_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close'] = pd.to_numeric(df['close'])
    df.set_index('open_time', inplace=True, drop=False)
    df['return'] = df['close'].pct_change() + 1
    df.iloc[0, df.columns.get_loc('return')] = 1 # set first datapoint to one
    df['cumulative_return'] = df['return'].cumprod()
    df['variance'] = df['close'].var()
    return df

def collect_data():
    symbols = Binance.perp_symbols
    failedOn_buffer = []
    def fetch_data(symbol, data):
        try:
            df = get_historical_data(symbol)
            data[symbol] = df
        except Exception as e:
            failedOn_buffer.append(symbol)
    data = {}
    threads = []
    for symbol in symbols:
        thread = threading.Thread(target=fetch_data, args=(symbol, data))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    
    print(f"**DEBUG**: Failed to fetch data for {len(failedOn_buffer)} symbols: {failedOn_buffer}")
    return data

def main():
    closes = collect_data()
    fig = plotly_closes(closes)
    fig.write_image('test_image.png')

if __name__=='__main__':
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        from Valera import alert
        alert()