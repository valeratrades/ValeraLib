# the default general-purpose package (try not to overload it)
from .Valera import *

# most used functions:
chk = TimePerfCounters()
dtf = decide_on_datetime_format
from .Binance import get_perp_symbols
bnpc = get_perp_symbols #//
rtd = round_time_down
tw = time_wrapper
sw = silent_wrapper
