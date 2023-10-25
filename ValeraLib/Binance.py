import os, json, requests, threading, pandas as pd, numpy as np, time
from datetime import datetime, timedelta

from .utils.DuckTypes import *

class Binance():
    def __init__(self):
        self.PerpSymbols:list[str] = getSymbols('perp')
        self.SpotSymbols:list[str] = getSymbols('spot')
        self.Symbols:list[str] = list(set(self.PerpSymbols+self.SpotSymbols))
       
    #TODO! rolling. preemptively calculate the needed queries, request all at once, then merge.
    def GetKlines(self, symbol:USDTSymbol, startTime:Timestamp, endTime:Timestamp, tf:BinanceTf, market:Market) -> Klines:
        symbol, startTimestamp, endTimestamp, tf, market = USDTSymbol(symbol), Timestamp(startTime), Timestamp(endTime), BinanceTf(tf), Market(market)
        assert startTimestamp.Ms < endTimestamp.Ms, "Your dumb ass has likely switched up endTime and startTime in arguments"
        assert symbol.V in self.Symbols, f"Unknown symbol: {symbol.V}"
        
        params = {
            "symbol": symbol.V,
            "interval": tf.V,
            "startTime": startTimestamp.Ms,
            "endTime": endTimestamp.Ms,
            # this is automatically scaled down when needed, but never up. If not stated, always will cap at 500.
            "limit": 1000,
        }
        url = market.BinanceBaseUrl + '/klines'

        raw_data = requests.get(url, params=params).json()
        df = pd.DataFrame(raw_data, columns=['open_ms', 'open', 'high', 'low', 'close', 'volume', 'close_ms', 'quote_asset_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
        
        df['close_dt'] = pd.to_datetime(df['close_ms'], unit='ms')
        df.set_index('close_dt', inplace=True, drop=False)
        df = df[['open', 'high', 'low', 'close', 'quote_asset_volume', 'trades']]
        df = df.rename(columns={"quote_asset_volume":"volume"})

        k = Klines(df)
        k.Market = market.V
        k.Tf = tf.V
        return k

    def CollectKlinesForSymbols(self, symbols:list[USDTSymbol], startTime:Timestamp, endTime:Timestamp, tf:BinanceTf, market:Market=None, full:bool=False) -> SymbolsKlines:
        """
        Takes 15-20s
        """
        if symbols == 'perp':
            symbols = self.PerpSymbols
        if symbols == 'spot':
            symbols = self.SpotSymbols
        if symbols == self.PerpSymbols and market==None:
            market = 'perp'
        if symbols == self.SpotSymbols and market==None:
            market = 'spot'
        assert market != None, "Provide `market:Market` argument too"
        _, _, _, _, _ = [USDTSymbol(s) for s in symbols], Timestamp(startTime), Timestamp(endTime), BinanceTf(tf), Market(market)
        failedOn_buffer = []
        errors = []
        def fetch_data(symbol, klinesDict):
            try:
                k = self.GetKlines(symbol, startTime, endTime, tf, market)
                if full:
                    k = self.GetFullData(k)
                klinesDict[symbol] = k
            except Exception as e:
                failedOn_buffer.append(symbol)
                errors.append(f"{type(e).__name__}: {str(e)}")
        klinesDict = {}
        threads = []
        for symbol in symbols:
            thread = threading.Thread(target=fetch_data, args=(symbol, klinesDict))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        
        if len(failedOn_buffer) != 0:
            print(f"**DEBUG**: Failed to fetch data for {len(failedOn_buffer)} symbols: {failedOn_buffer}")
        assert len(failedOn_buffer)<len(symbols)/2, f"Request failed. Errors encountered: {list(set(errors))}"
        sk = SymbolsKlines(klinesDict)
        return sk
    
    def GetFullData(k:Klines):
        k = Klines(k)
        k = loadNormVolume(k)
        return k
        
        
    def Dump(self, market: Market):
        #todo make it dump the object itself
        _ = Market(market)
        symbols = self.PerpSymbols if market=="perp" else self.SpotSymbols
        
        import inspect
        caller_frame = inspect.stack()[1]
        caller_filename_full = caller_frame.filename
        file_name = f'binance-{market}-pairs.json'
        caller_dir = os.path.dirname(caller_filename_full)
        if 'src' in os.listdir(caller_dir):
            file_name = 'src/' + file_name
        json.dump(symbols, open(file_name, 'w'))
        
def getSymbols(market: Market) -> list[str]:
    market = Market(market)
    """
    returns full list of USDT tickers from the specified market; f: ['BTCUSDT', ...]
    """
    
    url = market.BinanceBaseUrl + '/ticker/24hr'
    to_drop = ['USDC', 'BTCDOM', 'BTCST']
    
    r = requests.get(url)
    assert r.status_code == requests.codes.ok, f"get_perp_symbors()'s request failed with status code: {r.status_code}"
    data = r.json()
    symbols = [ticker['symbol'] for ticker in data if ticker['symbol'][-4:]=='USDT' and not ticker['symbol'][:-4] in to_drop]
    return symbols

def avVolumeCall(ticker, endTime, debug):
    if debug:
        from Valera import d
    base_url = 'https://fapi.binance.com/fapi/v1'
    params = {
        'symbol': ticker,
        'interval': '1h',
        'endTime': endTime,
        'limit': 30*24,
    }
    r = requests.get(base_url+'/klines', params=params).json()

    av_1s_volume = sum([float(item[7]) for item in r])/(30*24*60*60)
    print(f"DEBUG: av 1s volume: {av_1s_volume}") if debug else None
    return av_1s_volume
def loadNormVolume(k:Klines):
    k = Klines(k)
    m, _ = Market(k.Market), BinanceTf(k.Tf)
    baseUrl = m.BinanceBaseUrl
    bounds = (Timestamp(k.V.index[0]), Timestamp(k.V.index[-1]))
    
    params = {
        'symbol': k.Ticker,
        'interval': None,
        'endTime': None,
        'limit': 30*24,
    }
    
    # load 30d
    tf = BinanceTf('1h')
    timeBias_ms = 2*tf.Seconds*1000
    params['interval'], params['endTime'] = tf.V, bounds[0].Ms - timeBias_ms
    
    
    # load hours
    # load last 5m
    return k


if __name__=='__main__':
    try:
        b = Binance()
        out = b.CollectKlinesForSymbols(b.PerpSymbols, time.time()-60*24*24, time.time(), '5m')
        from pprint import pprint
        pprint(out)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        from Valera import alert
        alert()
