def despike(chainage, threshold=40):
    chainage = chainage.dropna()
    chainage, dates = SDS_transects.identify_outliers(
        chainage.tolist(), chainage.index.tolist(), threshold
    )
    return pd.Series(chainage, index=dates)


def get_trends(f):
    df = pd.read_csv(f)
    try:
        df.dates = pd.to_datetime(df.dates)
    except:
        print(f)
    if "sar" in f or "ber" in f:
        smoothed_filename = f.replace(".csv", "_smoothed.csv")
        try:
            df = pd.read_csv(smoothed_filename)
            df.dates = pd.to_datetime(df.dates)
        except:
            df.dates = pd.to_datetime(df.dates)
            df.set_index("dates", inplace=True)
            satname = df.satname
            df = df.drop(columns="satname").apply(despike, axis=0)
            df["satname"] = satname
            df.reset_index(names="dates").to_csv(
                f.replace(".csv", "_despiked.csv"), index=False
            )
            for transect_id in df.drop(columns="satname").columns:
                df[transect_id] = df[transect_id].rolling("180d", min_periods=1).mean()
            df.reset_index(names="dates", inplace=True)
            df.to_csv(f.replace(".csv", "_smoothed.csv"), index=False)
    df.index = (df.dates - df.dates.min()).dt.days / 365.25
    df.drop(columns=["dates", "satname", "Unnamed: 0"], inplace=True, errors="ignore")
    trends = []
    for transect_id in df.columns:
        sub_df = df[transect_id].dropna()
        if not len(sub_df):
            continue
        x = sub_df.index.to_numpy().reshape(-1, 1)
        y = sub_df
        linear_model = LinearRegression().fit(x, y)
        pred = linear_model.predict(x)
        trends.append(
            {
                "transect_id": transect_id,
                "trend": linear_model.coef_[0],
                "intercept": linear_model.intercept_,
                "n_points": len(df[transect_id]),
                "n_points_nonan": len(sub_df),
                "r2_score": r2_score(y, pred),
                "mae": mean_absolute_error(y, pred),
                "mse": mean_squared_error(y, pred),
                "rmse": root_mean_squared_error(y, pred),
            }
        )
    return pd.DataFrame(trends)


# trends = get_trends(sar_files.iloc[-1]).set_index("transect_id")
trends = pd.concat(process_map(get_trends, my_files)).set_index("transect_id")
len(trends)