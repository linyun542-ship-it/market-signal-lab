"""Generate additional charts from saved daily backtest returns."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def report_charts(frame, output, ticker):
    annual = frame[['strategy_return', 'benchmark_return']].groupby(frame.index.year).agg(lambda x: (1+x).prod()-1)*100
    fig, ax = plt.subplots(figsize=(10, 4.8))
    x = np.arange(len(annual))
    for i, (column, label, color) in enumerate([
        ('strategy_return', 'Strategy', '#247ba0'),
        ('benchmark_return', 'Buy and hold', '#ed8b36')]):
        bars = ax.bar(x+(i-.5)*.36, annual[column], .36, label=label, color=color)
        ax.bar_label(bars, fmt='%.1f%%', padding=4, fontsize=9)
    ax.set(xticks=x, xticklabels=annual.index, ylabel='Compounded return (%)', title=f'{ticker}: calendar-year return comparison')
    ax.axhline(0, color='#64748b', linewidth=.8)
    ax.legend(); ax.grid(axis='y', alpha=.15); ax.set_axisbelow(True); ax.margins(y=.2)
    fig.tight_layout(); fig.savefig(output/'annual_returns.png', dpi=160); plt.close(fig)
    monthly = frame.strategy_return.groupby(frame.index.to_period('M')).agg(lambda x: (1+x).prod()-1)*100
    years = sorted(set(monthly.index.year))
    grid = np.full((len(years), 12), np.nan)
    for period, value in monthly.items():
        grid[years.index(period.year), period.month-1] = value
    fig, ax = plt.subplots(figsize=(10, 4.5))
    bound = max(float(np.nanmax(np.abs(grid))), 1)
    img = ax.imshow(grid, cmap='RdYlGn', vmin=-bound, vmax=bound, aspect='auto')
    ax.set(xticks=range(12), xticklabels=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], yticks=range(len(years)), yticklabels=years, title=f'{ticker}: strategy monthly returns (%)')
    for row in range(len(years)):
        for col in range(12):
            if np.isfinite(grid[row,col]):
                ax.text(col,row,f'{grid[row,col]:.1f}',ha='center',va='center',color='white' if abs(grid[row,col]) > bound*.65 else '#172033',fontsize=9)
    fig.colorbar(img,ax=ax,label='Return (%)',shrink=.85)
    fig.tight_layout(); fig.savefig(output/'monthly_returns.png',dpi=160); plt.close(fig)


if __name__ == '__main__':
    from pathlib import Path
    directory = Path('results/qqq-daily')
    report_charts(pd.read_csv(directory/'backtest.csv',index_col='Date',parse_dates=True),directory,'QQQ')
