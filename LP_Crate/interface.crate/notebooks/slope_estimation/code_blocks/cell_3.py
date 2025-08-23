new_transects = transects[transects.index.str.startswith("nzd") & (transects.index > "nzd0562") & transects.beach_slope.isna()]
new_transects