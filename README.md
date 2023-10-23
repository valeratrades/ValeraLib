# Example:

```python
from ValeraLib import Binance, DataScience as ds
from ValeraLib.utils.DuckTypes import *

b = Binance()
sk:SymbolsKlines = b.CollectKlinesForSymbols('perp', time.time()-24*60*60, time.time(), '5m')
k:Klines = b.GetKlines('BTCUSDT', time.time()-24*60*60, time.time(), '5m', 'perp')

closes = sk.ToOpensDf()

fig = ds.plotly_closes(closes)
fig.write_image("test_image.png")
```