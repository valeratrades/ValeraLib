"""
All time values are by default ms timestamps
"""
import plotly.graph_objects as go, numpy as np, pandas as pd, time
from IPython.display import Image

def fromRaw(pandas_df):
    """
    do taking log, initializing at 1 and the rest here
    """
    df = pandas_df
    return df

def plotly_closes(dictOfDatetimePandasDfs):
    #todo move the stats into a separate block, then call this block on closes, and then pass the stats as a dict here, to then plot normally
    normalized_data = {symbol: df['close'] / df['close'].iloc[0] for symbol, df in dictOfDatetimePandasDfs.items()}
    normalized_df = pd.DataFrame(normalized_data)
    normalized_df = normalized_df.apply(np.log)

    performance = normalized_df.iloc[-1] - normalized_df.iloc[0]
    top_performers = performance.nlargest(5).index
    bottom_performers = performance.nsmallest(5).index
    
    mean_values = normalized_df.mean(axis=1)
    deviations_df = normalized_df.sub(mean_values, axis=0)
    flattened_deviations = deviations_df.values.flatten()
    variance = np.var(flattened_deviations, ddof=1) #* works, but unconvinient sizing - too many .00s
    kurtosis = pd.Series(flattened_deviations).kurt() #! meaningless due to **4 thingie, that gets skewed immediately on any outliers
    
    correlation_matrix = normalized_df.corr()
    mean_correlation = correlation_matrix.mean().mean()  #! pretty sure this is a very shitty method
    
    av_move = np.sum(performance)/len(performance)
    # </data-analysis>

    fig = go.Figure()

    def add_trace(*args):
        y, name, line, legend = args
        fig.add_trace(
                go.Scatter(
                    x=normalized_df.index,
                    y=y,
                    mode='lines',
                    name=name,
                    line=line,
                    showlegend=legend
                )
            )
    def add_performers(column):
        symbol = column[:-4]
        symbol.replace('1000', '', 1)
        sign = f"{performance[column]:+}"[0]
        change = f"{round(100*performance[column], 2):.2f}"
        change = change[1:] if change[0]=='-' else change
        name = f"{symbol:<5}{sign}{change:>5}%"
        add_trace(normalized_df[column], name, dict(width=2), True)
    def add_empty(name):
        add_trace([1]*len(normalized_df.index), name, dict(width=0), True)

    # <plotting>
    for column in normalized_df.columns:
        if column not in top_performers and column not in bottom_performers and column != 'BTCUSDT':
            add_trace(normalized_df[column], '', dict(width=1, color='grey'), False)
    for column in top_performers:
        add_performers(column)
    add_trace(normalized_df['BTCUSDT'], f"~BTC~ {round(100*performance['BTCUSDT'], 2):>5}", dict(width=5, color='gold'), True)
    for column in bottom_performers[::-1]:
        add_performers(column)
    add_empty('')
    add_empty(f"V:  {variance:.5f}")
    add_empty(f"K:  {round(kurtosis, 1)}")
    add_empty(f"C:  {round(mean_correlation, 2)}")
    add_empty(f"AV: {av_move*100:.5f}%")
    # </plotting>
    
    fig.update_layout(template='plotly_dark', autosize=True, margin=dict(l=0, r=0, b=0, t=0), font={"family":"Courier New, monospace"})
    fig.update_xaxes(range=[normalized_df.index.min(), normalized_df.index.max()])
    fig.update_yaxes(range=[normalized_df.min().min(), normalized_df.max().max()])

    return fig

if __name__=='__main__':
    try:
        from Binance import Binance
        b = Binance()
        data = b.CollectKlinesForSymbols('perp', time.time()-24*60*60, time.time(), '5m')
        plotly_closes(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        from Valera import alert
        alert()