vos_files = pd.Series(
    sorted(glob("csv_run7/*/time_series_tidally_corrected.csv"))
)
vos_files = vos_files[~vos_files.str.contains("nzd")]
vos_files