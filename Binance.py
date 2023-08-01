import os, json, requests

# <argument-duck-types>
class Market:
    def __init__(self, market_type):
        if market_type not in ['perp', 'spot']:
            raise ValueError("Valid options for market are 'perp' or 'spot'")
        self.market_type = market_type
# </argument-duck-types>

class Binance():
    # This is fucking genius: I'll have self.perp_symbols, self.spot_symbol and self.marg_symbols; then I can define self.functions for collecting data given symbols in the general case.
    def __init__(self):
        self.perp_symbols = get_symbols('perp')
        self.spot_symbors = get_symbols('spt')
        
        
    def dump(self, market: Market):
        symbols = self.perp_symbols if market=="perp" else self.spot_symbols
        
        import inspect
        caller_frame = inspect.stack()[1]
        caller_filename_full = caller_frame.filename
        file_name = 'binance-perp-pairs.json'
        caller_dir = os.path.dirname(caller_filename_full)
        if 'src' in os.listdir(caller_dir):
            file_name = 'src/' + file_name
        json.dump(symbols, open(file_name, 'w'))
        
def get_symbols(market: Market):
    """
    market can be "perp" or "spot"
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
    coins = [ticker['symbol'] for ticker in data if ticker['symbol'][-4:]=='USDT' and not ticker['symbol'][:-4] in to_drop]
    return coins

if __name__=='__main__':
    try:
        binance = Binance()
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        from Valera import alert
        alert()
