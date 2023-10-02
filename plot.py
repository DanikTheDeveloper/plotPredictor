import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from datetime import datetime
from scipy.stats import pearsonr
from concurrent.futures import ThreadPoolExecutor, as_completed


class SharePriceViewer:

    def __init__(self):
        self.start_time = datetime(2022, 1, 1)
        self.end_time = datetime.now()
        self.frequency = '1H'
        self.searchStart = None
        self.similarity_rate = 0
        self.window_size = 100
        self.df = self.generate_data()
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(bottom=0.3)
        self.vline = None  # Add this line to initialize vline as None
        self.setup_plot()
        self.slider, self.vline_slider, self.similarity_slider, self.button = self.create_widgets()
        plt.show()

    def generate_data(self):
        date_rng = pd.date_range(start=self.start_time, end=self.end_time, freq=self.frequency)
        prices = np.random.randint(100, 500, size=(len(date_rng),))
        df = pd.DataFrame(date_rng, columns=['date'])
        df['price'] = prices
        return df

    def similarity(self, start, end, target):
        pattern = self.df['price'][start:end].values
        target_pattern = self.df['price'][target:target + (end - start)].values
        if len(pattern) != len(target_pattern):
            return 0
        correlation, _ = pearsonr(pattern, target_pattern)
        similarity = max(0, correlation * 100)
        return similarity

    def setup_plot(self):
        self.ax.scatter(self.df['date'], self.df['price'])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Price')
        self.ax.set_title('Share Price Over Time')
        self.ax.set_xlim(self.df['date'][0], self.df['date'][self.window_size])
        self.vline = self.ax.axvline(x=self.df['date'][0], color='red')

    def create_widgets(self):
        axslider = plt.axes([0.2, 0.2, 0.65, 0.03])
        slider = Slider(axslider, 'Date', 0, len(self.df) - self.window_size, valinit=0, valstep=1)
        slider.on_changed(self.update)

        axvline_slider = plt.axes([0.2, 0.15, 0.65, 0.03])
        vline_slider = Slider(axvline_slider, 'Select Time', 0, self.window_size, valinit=0, valstep=1)
        vline_slider.on_changed(self.update_vline)

        axsimilarity_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
        # Adjust the minimum value to 70
        similarity_slider = Slider(axsimilarity_slider, 'Similarity', 70, 100, valinit=70, valstep=1)

        axbutton = plt.axes([0.8, 0.025, 0.1, 0.04])
        button = Button(axbutton, 'Select Time')
        button.on_clicked(self.select)

        return slider, vline_slider, similarity_slider, button

    def update(self, val):
        pos = int(self.slider.val)
        end_pos = min(pos + self.window_size, len(self.df) - 1)
        self.ax.set_xlim(self.df['date'][pos], self.df['date'][end_pos])

    def update_vline(self, val):
        pos = int(self.slider.val)
        vline_index = min(pos + int(self.vline_slider.val), len(self.df) - 1)
        self.vline.set_xdata(self.df['date'][vline_index]) 

    def select(self, event):
        pos = int(self.slider.val)
        self.searchStart = pos + int(self.vline_slider.val)
        self.similarity_rate = int(self.similarity_slider.val)
        print(f"Selected Time: {self.df['date'][self.searchStart]}")
        self.highlight_similar(self.searchStart, pos + self.window_size, self.similarity_rate)

    def highlight_similar(self, start, end, rate):
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.similarity, start, end, i): i for i in range(len(self.df) - (end - start))}
            for future in as_completed(futures):
                i = futures[future]
                sim = future.result()
                if sim >= rate:
                    self.ax.axvspan(self.df['date'][i], self.df['date'][i + (end - start)], edgecolor='yellow', 
                                    facecolor='none', lw=2)
                    self.ax.text(self.df['date'][i], self.df['price'].max(), f'{int(sim)}%', fontsize=8, ha='left')
        self.fig.canvas.draw()


if __name__ == '__main__':
    SharePriceViewer()
