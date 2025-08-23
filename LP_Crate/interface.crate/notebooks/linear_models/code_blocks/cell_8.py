df = pd.read_csv("data/sar0939/transect_time_series.csv")
df.dates = pd.to_datetime(df.dates)
df.set_index("dates", inplace=True)
(df["sar0939-0000"] - 93).plot()