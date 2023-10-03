import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.stats import pearsonr
import yfinance as yf
import mplfinance as mpf
from matplotlib.dates import date2num

def fetch_yahoo_finance_data(symbol, interval, period):
    stock = yf.Ticker(symbol)
    data = stock.history(period=period, interval=interval)
    data.reset_index(inplace=True)
    data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock splits']
    data = data[['datetime', 'open', 'high', 'low', 'close']]
    data['datetime'] = pd.to_datetime(data['datetime'])
    data.set_index('datetime', inplace=True)
    return data


class SharePriceViewer:

    def __init__(self, symbol, interval, period):
        self.fig, self.ax = plt.subplots(figsize=(10, 5))  
        self.symbol = symbol
        self.frequency = interval
        self.searchStart = None
        self.similarity_rate = 0
        self.window_size = 100
        self.df = fetch_yahoo_finance_data(symbol, interval, period)
        plt.subplots_adjust(bottom=0.35)
        self.vline = None
        self.setup_plot()
        self.create_widgets()
        plt.show()

    def similarity(self, start, end, target):
        pattern = self.df['close'][start:end].values
        target_pattern = self.df['close'][target:target + (end - start)].values
        if len(pattern) != len(target_pattern):
            return 0
        correlation, _ = pearsonr(pattern, target_pattern)
        similarity = max(0, correlation * 100)
        return similarity

    def setup_plot(self):
        if len(self.df) > 0:
            self.ax.set_xlabel('Time')
            self.ax.set_title('Candlestick Chart Over Time')
            end_index = min(self.window_size, len(self.df) - 1)
            self.ax.set_xlim(self.df.index[0], self.df.index[end_index])
            self.vline = self.ax.axvline(x=self.df.index[0], color='red')
            for i, row in self.df.iterrows():
                color = 'g' if row['close'] >= row['open'] else 'r'
                self.ax.plot([date2num(i), date2num(i)], [row['low'], row['high']], color=color)
                self.ax.plot([date2num(i), date2num(i)], [row['open'], row['close']], linewidth=6, color=color)
            
            self.ax.xaxis_date()
            plt.xticks(rotation=45)
            self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        else:
            print("Error: DataFrame is empty.")

    def create_widgets(self):
        axslider = plt.axes([0.2, 0.2, 0.65, 0.03])
        self.slider = Slider(axslider, 'Date', 0, len(self.df) - self.window_size, valinit=0, valstep=1)
        self.slider.on_changed(self.update)

        axvline_slider = plt.axes([0.2, 0.15, 0.65, 0.03])
        self.vline_slider = Slider(axvline_slider, 'Select Time', 0, self.window_size, valinit=0, valstep=1)
        self.vline_slider.on_changed(self.update_vline)

        axsimilarity_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
        self.similarity_slider = Slider(axsimilarity_slider, 'Similarity', 70, 100, valinit=70, valstep=1)

        axbutton = plt.axes([0.8, 0.025, 0.1, 0.04])
        self.button = Button(axbutton, 'Select Time')
        self.button.on_clicked(self.select)

        axbutton_clear = plt.axes([0.68, 0.025, 0.1, 0.04])
        self.button_clear = Button(axbutton_clear, 'Clear Result')
        self.button_clear.on_clicked(self.clear_result)
    
    def clear_result(self, event):
        for patch in self.ax.patches:
            patch.remove()
        for text in self.ax.texts:
            text.remove()
        self.fig.canvas.draw()


    def update(self, val):
        pos = int(self.slider.val)
        end_pos = min(pos + self.window_size, len(self.df) - 1)
        self.ax.set_xlim(self.df.index[pos], self.df.index[end_pos])

    def update_vline(self, val):
        pos = int(self.slider.val)
        vline_index = min(pos + int(self.vline_slider.val), len(self.df) - 1)
        self.vline.set_xdata([self.df.index[vline_index]])

    def select(self, event):
        pos = int(self.slider.val)
        self.searchStart = pos + int(self.vline_slider.val)
        self.similarity_rate = int(self.similarity_slider.val)
        print(f"Selected Time: {self.df.index[self.searchStart]}")
        self.highlight_similar(self.searchStart, pos + self.window_size, self.similarity_rate)

    def highlight_similar(self, start, end, rate):
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.similarity, start, end, i): i for i in range(len(self.df) - (end - start))}
            for future in as_completed(futures):
                i = futures[future]
                sim = future.result()
                if sim >= rate:
                    self.ax.axvspan(self.df.index[i], self.df.index[i + (end - start)], edgecolor='yellow', 
                                    facecolor='none', lw=2)
                    self.ax.text(self.df.index[i], self.df['close'].max(), f'{int(sim)}%', fontsize=8, ha='left')
        self.fig.canvas.draw()


if __name__ == '__main__':
    interval = "15m"
    period = "1mo"
    symbol = input("Enter the stock symbol (e.g., MSFT, BTC-USD): ")
    SharePriceViewer(symbol, interval, period)
