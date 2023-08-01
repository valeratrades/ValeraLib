import os, json

class Binance():
    # This is fucking genius: I'll have self.perp_symbols, self.spot_symbol and self.marg_symbols; then I can define self.functions for collecting data given symbols in the general case.
    def __init__(self):
        self.perp_symbols = get_binance_perp_symbols()
        
    def dump(self, market):
        """
        market can be "perp", "spot", "marg"
        #! as of this moment, implemented only "perp"
        """
        symbols = self.perp_symbols
        import inspect
        caller_frame = inspect.stack()[1]
        caller_filename_full = caller_frame.filename
        file_name = 'binance-perp-pairs.json'
        caller_dir = os.path.dirname(caller_filename_full)
        if 'src' in os.listdir(caller_dir):
            file_name = 'src/' + file_name
        json.dump(symbols, open(file_name, 'w'))
        

def get_binance_perp_symbols():
    """
    returns list of listed perps; f: ['BTCUSDT', ...]
    """
    import requests
    url = 'https://fapi.binance.com/fapi/v1/ticker/24hr'
    r = requests.get(url)
    assert r.status_code == requests.codes.ok, f"dump_binance_perf_coins()'s request failed with status code: {r.status_code}"
    data = r.json()
    to_drop = ['USDC', 'BTCDOM', 'BTCST']
    coins = [ticker['symbol'] for ticker in data if ticker['symbol'][-4:]=='USDT' and not ticker['symbol'][:-4] in to_drop]
    return coins