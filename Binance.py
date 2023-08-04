import os, json, requests, threading, pandas as pd, numpy as np, time
from datetime import datetime, timedelta

from .src.DuckTypes import *

class Binance():
    def __init__(self):
        self.perp_symbols = getSymbols('perp')
        self.spot_symbols = getSymbols('spot')
        self.symbols = list(set(self.perp_symbols+self.spot_symbols))
        
    def GetKlines(self, symbol:USDTSymbol, startTime:Timestamp, endTime:Timestamp, tf:BinanceTf, market:Market) -> Klines:
        symbol, startTimestamp, endTimestamp, tf, market = USDTSymbol(symbol), Timestamp(startTime), Timestamp(endTime), BinanceTf(tf), Market(market)
        assert startTimestamp.Unix_ms < endTimestamp.Unix_ms, "Your dumb ass has likely switched up endTime and startTime in arguments"
        assert symbol.V in self.symbols, f"Unknown symbol: {symbol.V}"
        
        params = {
            "symbol": symbol.V,
            "interval": tf.V,
            "startTime": startTimestamp.Unix_ms,
            "endTime": endTimestamp.Unix_ms,
        }
        url = market.BinanceBaseUrl + '/klines'

        raw_data = requests.get(url, params=params).json()
        df = pd.DataFrame(raw_data, columns=['open_ms', 'open', 'high', 'low', 'close', 'volume', 'close_ms', 'quote_asset_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
        
        df['open_time'] = pd.to_datetime(df['open_ms'], unit='ms')
        df.set_index('open_time', inplace=True, drop=False)
        df = df[['open', 'high', 'low', 'close', 'quote_asset_volume', 'trades']]
        df = df.rename(columns={"quote_asset_volume":"volume"})
        
        #todo: these things move out of the df and outside into a separate model
        # df['close'] = pd.to_numeric(df['close'])
        # df['return'] = df['close'].pct_change() + 1
        # df.iloc[0, df.columns.get_loc('return')] = 1 # set first datapoint to one
        # df['cumulative_return'] = df['return'].cumprod()
        # df['variace'] = df['close'].var()
        
        k = Klines(df)
        k.Market = market.V
        k.Tf = tf.V
        return k
        
    def CollectKlinesForSymbols(self, symbols:list[USDTSymbol], startTime:Timestamp, endTime:Timestamp, tf:BinanceTf, market:Market=None) -> SymbolsKlines:
        if symbols == 'perp':
            symbols = self.perp_symbols
        if symbols == 'spot':
            symbols = self.spot_symbols
        if symbols == self.perp_symbols and market==None:
            market = 'perp'
        if symbols == self.spot_symbols and market==None:
            market = 'spot'
        assert market != None, "Provide `market:Market` argument too"
        _, _, _, _, _ = [USDTSymbol(s) for s in symbols], Timestamp(startTime), Timestamp(endTime), BinanceTf(tf), Market(market)
        failedOn_buffer = []
        errors = []
        def fetch_data(symbol, klinesDict):
            try:
                k = self.GetKlines(symbol, startTime, endTime, tf)
                klinesDict[symbol] = k
            except Exception as e:
                failedOn_buffer.append(symbol)
                errors.append(e)
        klinesDict = {}
        threads = []
        for symbol in symbols:
            thread = threading.Thread(target=fetch_data, args=(symbol, klinesDict))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        
        print(f"**DEBUG**: Failed to fetch data for {len(failedOn_buffer)} symbols: {failedOn_buffer}")
        assert len(failedOn_buffer)<len(symbols)/2, f"Request failed. Errors encountered: {list(set(errors))}"
        return klinesDict
        
    def Dump(self, market: Market):
        _ = Market(market)
        symbols = self.perp_symbols if market=="perp" else self.spot_symbols
        
        import inspect
        caller_frame = inspect.stack()[1]
        caller_filename_full = caller_frame.filename
        file_name = f'binance-{market}-pairs.json'
        caller_dir = os.path.dirname(caller_filename_full)
        if 'src' in os.listdir(caller_dir):
            file_name = 'src/' + file_name
        json.dump(symbols, open(file_name, 'w'))
        
def getSymbols(market: Market) -> list[USDTSymbol]:
    _ = Market(market)
    """
    returns full list of USDT tickers from the specified market; f: ['BTCUSDT', ...]
    """
        
    urls = {
        'perp': 'https://fapi.binance.com/fapi/v1/ticker/24hr',
        'spot': 'https://api.binance.com/api/v3/ticker/24hr'
    }
    
    url = urls[market]
    to_drop = ['USDC', 'BTCDOM', 'BTCST']
    
    r = requests.get(url)
    assert r.status_code == requests.codes.ok, f"get_perp_symbors()'s request failed with status code: {r.status_code}"
    data = r.json()
    symbols = [ticker['symbol'] for ticker in data if ticker['symbol'][-4:]=='USDT' and not ticker['symbol'][:-4] in to_drop]
    return symbols

if __name__=='__main__':
    try:
        b = Binance()
        out = b.CollectKlinesForSymbols(b.perp_symbols, time.time()-60*24*24, time.time(), '5m')
        from pprint import pprint
        pprint(out)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        from Valera import alert
        alert()
