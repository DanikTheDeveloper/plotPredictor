import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from datetime import datetime
from scipy.stats import pearsonr

# Variables
start_time = datetime(2022, 1, 1)  # Start time
end_time = datetime.now()  # End time
frequency = '1H'  # Frequency (1 hour)
searchStart = None  # The selected timestamp variable
similarity_rate = 0  # Similarity rate


# Generate sample data
date_rng = pd.date_range(start=start_time, end=end_time, freq=frequency)
prices = np.random.randint(100, 500, size=(len(date_rng),))

df = pd.DataFrame(date_rng, columns=['date'])
df['price'] = prices

# Calculate differences
df['diff'] = df['price'].diff().fillna(0)


# Pattern similarity function
def similarity(start, end, target):
    pattern = df['price'][start:end].values
    target_pattern = df['price'][target:target + (end - start)].values
    if len(pattern) != len(target_pattern):
        return 0
    correlation, _ = pearsonr(pattern, target_pattern)
    similarity = max(0, correlation * 100)
    return similarity


# Plot
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.55)
scatter = ax.scatter(df['date'], df['price'])

# Set labels and title
ax.set_xlabel('Time')
ax.set_ylabel('Price')
ax.set_title('Share Price Over Time')

# Define a viewing window size
window_size = 100  # view 100 data points at a time

# Set the initial x-axis limits
ax.set_xlim(df['date'][0], df['date'][window_size])

# Add a vertical line to indicate the selected timestamp
vline = ax.axvline(x=df['date'][0], color='red')

# Make the x-axis scrollable
axslider = plt.axes([0.2, 0.3, 0.65, 0.03])
slider = Slider(axslider, 'Date', 0, len(df) - window_size, valinit=0, valstep=1)

# Add another slider to control the vertical line
axvline_slider = plt.axes([0.2, 0.2, 0.65, 0.03])
vline_slider = Slider(axvline_slider, 'Select Time', 0, window_size, valinit=0, valstep=1)

# Add another slider to control similarity rate
axsimilarity_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
similarity_slider = Slider(axsimilarity_slider, 'Similarity', 0, 100, valinit=0, valstep=1)


def update(val):
    pos = int(slider.val)
    end_pos = min(pos + window_size, len(df) - 1)  # Ensure the index does not exceed the DataFrame length
    ax.set_xlim(df['date'][pos], df['date'][end_pos])


slider.on_changed(update)


def update_vline(val):
    pos = int(slider.val)
    vline_index = min(pos + int(vline_slider.val), len(df) - 1)  # Ensure the index does not exceed the DataFrame length
    vline.set_xdata(df['date'][vline_index])


vline_slider.on_changed(update_vline)

# Add a button for selecting the timestamp
axbutton = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(axbutton, 'Select Time')


def select(event):
    global searchStart, similarity_rate
    pos = int(slider.val)
    searchStart = pos + int(vline_slider.val)
    similarity_rate = int(similarity_slider.val)
    print(f"Selected Time: {df['date'][searchStart]}")
    highlight_similar(searchStart, pos + window_size, similarity_rate)


def highlight_similar(start, end, rate):
    for i in range(len(df) - (end - start)):
        sim = similarity(start, end, i)
        if sim >= rate:
            ax.axvspan(df['date'][i], df['date'][i + (end - start)], edgecolor='yellow', facecolor='none', lw=2)
            ax.text(df['date'][i], df['price'].max(), f'{int(sim)}%', fontsize=8, ha='left')
    fig.canvas.draw()


button.on_clicked(select)

plt.show()
