%load_ext autotime
import geopandas as gpd
import pandas as pd
import numpy as np
from tqdm.auto import tqdm
from glob import glob
from shapely.geometry import LineString, Point
import folium
import matplotlib.pyplot as plt
import pytz
from datetime import datetime, timedelta
pd.set_option('display.max_columns', None)
import SDS_slope