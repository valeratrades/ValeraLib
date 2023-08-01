from Binance import Binance
from Valera import dbg

from src.DuckTypes import *

b = Binance()
k = b.GetKlines('BTCUSDT', time.time()-24*60*60, time.time(), '5m', 'perp')
k.Normalize()
from pprint import pprint
pprint(k)