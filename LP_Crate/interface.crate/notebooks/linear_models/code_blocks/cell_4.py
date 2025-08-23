my_files = pd.Series(
    sorted(glob("data/*/transect_time_series_tidally_corrected.csv"))
)
my_files