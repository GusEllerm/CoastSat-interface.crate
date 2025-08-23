transects = transects.join(trends.loc[:, ~trends.columns.isin(transects.columns)])
transects