import threading, os, requests, pandas as pd, numpy as np, time
from datetime import datetime, timedelta

from DataScience import plotly_closes
from Binance import Binance
b = Binance()
from Valera import dbg

def main():
    symbolsKlines = b.CollectKlinesForSymbols('perp', time.time()-24*60*60, time.time(), '5m')
    fig = plotly_closes(symbolsKlines)
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
