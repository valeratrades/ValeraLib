import time, pandas as pd, numpy as np
from datetime import datetime, timedelta

from Valera import dbg

"""
Each class could be called upon to:
. create an instance
    or
. do a DuckType check, returning the value or the main value of the class itself if it is passed
As such, `@classmethod check(cls, value):` is implemented in every one of these

All the values meant to be exported are starting with a Capital letter
The main value is always `V`

As per usage, it is custom for single-item variables to stay not as instances, but as values.
However, anything more complex is usually passed around as class instances
"""

class Market:
    def __init__(self, market):
        self.V = self.__class__.check(market)
        self.BinanceBaseUrl = 'https://fapi.binance.com/fapi/v1' if self.V=='perp' else 'https://api.binance.com/api/v3'
    @classmethod
    def check(cls, value):
        if isinstance(value, cls):
            return value.V
        if value not in ['perp', 'spot']:
            raise ValueError("Valid options for market are 'perp' or 'spot'")
        return value
        
class USDTSymbol:
    def __init__(self, symbol):
        self.V = self.__class__.check(symbol)
        self.Coin = self.V[:-4].lower()
    @classmethod
    def check(cls, value):
        if isinstance(value, cls):
            return value.V
        if not value.isupper():
            raise ValueError(f"Provided symbol is of incorrect format: {value}")
        if not value.endswith('USDT'):
            raise ValueError(f"USDTSymbol must be quoted against USDT")
        return value
    
class BinanceTf:
    def __init__(self, tf):
        self.V = self.__class__.check(tf)
        self.Seconds = self.getSeconds(self.V)
    @classmethod
    def check(cls, value):
        if isinstance(value, cls):
            return value.V
        if value not in ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']:
            raise ValueError(f"Invalid tf format. Pass a valide BinanceAPI timeframe, not: {value}")
        return value
    def getSeconds(self, tf):
        num = int(tf[:-1])
        interval = tf[-1]
        map = {
            'm': 60,
            'h': 60*60,
            'd': 24*60*60,
            'w': 7*24*60*60,
            'M': 30*7*24*60*60
        }
        multiplier = map.get(interval)
        seconds = num*multiplier
        return seconds
    
class Timestamp:
    def __init__(self, timestamp):
        self.V = self.__class__.check(timestamp)
        self.Unix_ns = self.convertAnyToUnixNs(self.V)
        self.Unix_s = int(round(self.Unix_ns/1_000_000_000))
        self.Unix_ms = int(round(self.Unix_ns/1_000_000))
        self.Unix_us = int(round(self.Unix_ns/1_000))
        self.Datetime = datetime.fromtimestamp(self.Unix_ns/1_000_000_000)
        self.Isoformat = self.Datetime.isoformat()
    @classmethod
    def check(cls, value):
        if isinstance(value, cls):
            return value.V # returning the original Timestamp value, because there is no main value here
        return value
    def convertAnyToUnixNs(self, timestamp):
        unix_ns = None
        # checks if isoformat
        try:
            dt = datetime.fromisoformat(timestamp)
            unix_ns = dt.timestamp() * 1_000_000_000
        except:pass
        # checks if datetime
        try: unix_ns = timestamp.timestamp()*1_000_000_000
        except:pass
        # checks if unix
        try:
            if len(str(round(timestamp))) == 10:
                unix_ns = timestamp * 1_000_000_000
            if len(str(round(timestamp))) == 13:
                unix_ns = timestamp * 1_000_000
            if len(str(round(timestamp))) == 16:
                unix_ns = timestamp * 1_000
            if len(str(round(timestamp)))==19:
                unix_ns = timestamp
            assert 0 <= unix_ns/1_000_000_000 <= time.time()
        except:pass
            
        assert unix_ns != None, f"Provided timestamp type isn't supported.\nProvided: {timestamp}\nSupported: [unix_s, unix_ms, unix_us, unix_ns, datetime, isoformat], where only isoformat can be string"
        return unix_ns
    
class ClosesDf:
    pass

class Klines:
    def __init__(self, klinesDf):
        self.V = self.__class__.check(klinesDf)
        self.Market:Market = None
        self.Tf:BinanceTf = None
        self.Full = None #* can be 'perp', 'spot' or None
        # if .Full != None, means we'll have additional columns, that consitute 'perp' Full or 'spot' Full.
    @classmethod
    def check(cls, value):
        if isinstance(value, cls):
            return value.V
        assert isinstance(value, pd.DataFrame)
        assert isinstance(value.index[0], datetime)
        mandatoryColumns = ['open', 'high', 'low', 'close', 'volume']
        for column in mandatoryColumns:
            assert column in value.columns
        value[mandatoryColumns] = value[mandatoryColumns].apply(pd.to_numeric)
        return value
    def collectFullData(self):
        assert (self.Market != None and self.Tf == None), "Klines object should have both self.Market and self.Tf specified for this function to be collable"
        _, _ = Market.check(self.Market), BinanceTf.check(self.Tf)
            
    def Normalize(self, dtTimestamp:Timestamp=None): #!
        df = self.V
        zeroIndex = df.index[0] if dtTimestamp == None else Timestamp(dtTimestamp).datetime
        columns = ['open', 'high', 'low', 'close', 'volume', 'oi', 'lsr']
        dbg(df.columns, 'open' in df.columns)
        for column in columns:
            if column in df.columns:
                zeroValue = df.loc[zeroIndex, column]
                df.loc[column] = df.loc[column].apply(lambda x: round(np.log( x /zeroValue)*100, 3)-100)
                
class SymbolsKlines:
    def __init__(self, klinesDict):
        self.V = self.__class__.check(klinesDict)
    @classmethod
    def check(cls, value):
        if isinstance(value, cls):
            return value.V
        assert isinstance(value, dict)
        assert len(value) >= 1
        for symbol, df in value.items():
            _, _ = USDTSymbol(symbol), Klines(df)
        return value 
    def Normalize(self, dtTimestamp:Timestamp=None):
        for symbol, klinesDf in self.V.items():
            klinesDf.Normalize(dtTimestamp)
    def ToOpensDf(self):
        raise "Not implemented yet"
        klinesDict = self.V
        # here we deal with Klines objects inside and turn the thing into opensDf
        opensDf = None
        return opensDf