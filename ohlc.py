import datetime as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc

import data_loader

plt.style.use("fivethirtyeight")


def indicator_chart(symbol, start=dt.datetime(2020, 7, 1), smas=(10, 30, 50, 210)):
    start = start - dt.timedelta(days=max(smas))
    now = dt.datetime.now()

    df = data_loader.load_price_history(symbol, start, now)

    date_delta = df.index[-1] - df.index[0]

    smas = [sma for sma in smas if sma < date_delta.days / 2]

    fig, ax = plt.subplots()
    fig.set_size_inches(32, 18)

    for sma in smas:
        df[f"SMA_{sma}"] = df["Adj Close"].rolling(window=sma).mean()

    # Bollinger bands
    bb_period = 15  # moving average
    std_dev = 2
    df[f"SMA_{bb_period}"] = df["Adj Close"].rolling(window=bb_period).mean()
    df["std_dev"] = df["Adj Close"].rolling(window=bb_period).std()
    df["lower_band"] = df[F"SMA_{bb_period}"] - (std_dev * df["std_dev"])  # upper Bollinger band
    df["upper_band"] = df[F"SMA_{bb_period}"] + (std_dev * df["std_dev"])  # lower Bollinger band
    df["Date"] = mdates.date2num(df.index)

    # 10.4.4 stochastic
    period = 10
    K = 4
    D = 4
    df["rol_high"] = df["High"].rolling(window=period).max()  # high of period
    df["rol_low"] = df["High"].rolling(window=period).min()  # low of period
    df["stok"] = ((df["Adj Close"] - df["rol_low"]) / (df["rol_high"] - df["rol_low"])) * 100  # 10.1
    df["K"] = df["stok"].rolling(window=K).mean()  # 10.4
    df["D"] = df["K"].rolling(window=D).mean()  # 10.4.4
    df["GD"] = df["K"].rolling(window=D).mean()  # green dots
    ohlc = []

    df = df.iloc[max(smas):]

    green_dot_date = []
    green_dot = []
    last_K = 0
    last_D = 0
    last_low = 0
    last_close = 0
    last_low_bb = 0

    # Iterate through price history creating candlesticks and green/blue dots

    for i in df.index:
        candlestick = df["Date"][i], df["Open"][i], df["High"][i], df["Low"][i], df["Adj Close"][i]
        ohlc.append(candlestick)

        # Green dot
        if df["K"][i] > df["D"][i] and last_K < last_D and last_K < 60:

            if 30 in smas and 210 in smas and df["High"][i] > df["SMA_30"][i] and df["High"][i] > df["SMA_210"][i]:
                color = "chartreuse"
            else:
                color = "green"

            plt.plot(df["Date"][i], df["High"][i], marker="o", ms=10, ls="", color=color)

            green_dot_date.append(i)
            green_dot.append(df["High"][i])

            # Lower Bollinger Band Bounce
        if ((last_low < last_low_bb) or (df["Low"][i] < df["lower_band"][i])) and (
                df["Adj Close"][i] > last_close and df["Adj Close"][i] > df["lower_band"][i]) and last_K < 60:
            plt.plot(df["Date"][i], df["Low"][i], marker="o", ms=10, ls="", color="blue")  # plot blue dot

            # store values
        last_K = df["K"][i]
        last_D = df["D"][i]
        last_low = df["Low"][i]
        last_close = df["Adj Close"][i]
        last_low_bb = df["lower_band"][i]

    # Plot moving averages and BBands
    for sma in smas:  # This for loop calculates the EMAs for te stated periods and appends to dataframe
        df[f"SMA_{sma}"].plot(label=f"{sma} SMA")
    df["upper_band"].plot(label="Upper Band", color="lightgray")
    df["lower_band"].plot(label="Lower Band", color="lightgray")

    # plot candlesticks
    candlestick_ohlc(ax, ohlc, width=0.75, colorup="k", colordown="r", alpha=0.75)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%B %d"))  # change x axis back to datestamps
    ax.xaxis.set_major_locator(mticker.MaxNLocator(8))  # add more x axis labels
    plt.tick_params(axis="x", rotation=45)  # rotate dates for readability

    # Pivot Points
    pivots = []  # Stores pivot values
    dates = []  # Stores Dates corresponding to those pivot values
    counter = 0  # Will keep track of whether a certain value is a pivot
    lastPivot = 0  # Will store the last Pivot value

    value_range = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    date_range = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for i in df.index:

        current_max = max(value_range, default=0)
        value = np.round(df["High"][i], 2)

        value_range = value_range[1:9]
        date_range = date_range[1:9]

        value_range.append(value)
        date_range.append(i)

        if current_max == max(value_range, default=0):
            counter += 1
        else:
            counter = 0

        if counter == 5:
            last_pivot = current_max
            date_loc = value_range.index(last_pivot)
            last_date = date_range[date_loc]

            pivots.append(last_pivot)
            dates.append(last_date)

    timeD = dt.timedelta(days=30)  # Sets length of dotted line on chart

    for index in range(len(pivots)):  # Iterates through pivot array

        # print(str(pivots[index])+": "+str(dates[index])) #Prints Pivot, Date couple
        plt.plot_date([dates[index] - (timeD * .075), dates[index] + timeD],  # Plots horizontal line at pivot value
                      [pivots[index], pivots[index]], linestyle="--", linewidth=2, marker=",", color="green")
        plt.annotate(str(pivots[index]), (mdates.date2num(dates[index]), pivots[index]), xytext=(-10, 7),
                     textcoords="offset points", fontsize=14, arrowprops=dict(arrowstyle="-|>"))

    plt.xlabel("Date")  # set x axis label
    plt.ylabel("Price")  # set y axis label
    plt.title(symbol + " - Daily")  # set title
    plt.ylim(df["Low"].min(), df["High"].max() * 1.05)  # add margins
    # plt.yscale("log")
    plt.legend(loc="upper left")
    plt.savefig(f"out/charts/{symbol}_chart_indicators.png", dpi=300)