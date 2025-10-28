%reload_ext autotime
import geopandas as gpd
import pandas as pd
from glob import glob
from sklearn.linear_model import LinearRegression
from tqdm.auto import tqdm
from tqdm.contrib.concurrent import process_map
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, root_mean_squared_error
from coastsat import SDS_transects
pd.options.plotting.backend = "plotly"