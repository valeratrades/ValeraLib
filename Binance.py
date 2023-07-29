import os, json

class Binance():
    # I'm thinking that could be a better option for multiple interconnected api calls. It is very probably that I'm just being a dumbass, though, so don't be afraid to delete.
    def __init__(self):
        self.perp_coins = get_binance_perp_coins()

def get_binance_perp_coins(dump=False):
    # returns list of listed perps; f: ['BTCUSDT', ...]
    import requests
    url = 'https://fapi.binance.com/fapi/v1/ticker/24hr'
    r = requests.get(url)
    assert r.status_code == requests.codes.ok, f"dump_binance_perf_coins()'s request failed with status code: {r.status_code}"
    data = r.json()
    to_drop = ['USDC', 'BTCDOM', 'BTCST']
    coins = [ticker['symbol'] for ticker in data if ticker['symbol'][-4:]=='USDT' and not ticker['symbol'][:-4] in to_drop]
    if dump:
        import inspect
        caller_frame = inspect.stack()[1]
        caller_filename_full = caller_frame.filename
        file_name = 'binance-perp-pairs.json'
        caller_dir = os.path.dirname(caller_filename_full)
        if 'src' in os.listdir(caller_dir):
            file_name = 'src/' + file_name
        json.dump(coins, open(file_name, 'w'))
    else:
        return coins
    return 200