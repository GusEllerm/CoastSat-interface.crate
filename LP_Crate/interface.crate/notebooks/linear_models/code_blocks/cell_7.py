f = files[files.str.contains("sar1026")].iloc[0]
# despiked_filename = f.replace(".csv", "_tidally_corrected.csv")
df = pd.read_csv(f)
df.dates = pd.to_datetime(df.dates)
df.set_index("dates", inplace=True)
display(df.columns)
import matplotlib.pyplot as plt

transect_id = "sar1026-0007"


def custom_mean(window):
    return window[window.between(window.quantile(0.25), window.quantile(0.75))].mean()


pd.DataFrame(
    {
        "raw": df[transect_id],
        "rolling 90d mean": df[transect_id].rolling("90d", min_periods=1).mean(),
        "rolling 180d mean": df[transect_id].rolling("180d", min_periods=1).mean(),
        "rolling 90d custom mean": df[transect_id]
        .rolling("90d", min_periods=1)
        .apply(custom_mean),
        "rolling 180d custom mean": df[transect_id]
        .rolling("180d", min_periods=1)
        .apply(custom_mean),
        # "rolling 365d": df[transect_id].rolling("365d", min_periods=1).mean(),
    },
    index=df.index,
).plot()