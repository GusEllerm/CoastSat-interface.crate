if len(new_transects):
  for site_id in tqdm(new_transects.site_id.unique()):
    df = pd.read_csv(f"data/{site_id}/transect_time_series.csv")
    df.index = pd.to_datetime(df.dates)
    df.drop(columns=["dates", "satname"], inplace=True)
    tides = pd.read_csv("data/{site_id}/tides.csv")
    tides.dates = pd.to_datetime(tides.dates)
    tides.set_index("dates", inplace=True)
    assert all(pd.to_datetime(df.index).round("10min") == tides.index)
    # slope estimation settings
    days_in_year = 365.2425
    seconds_in_day = 24*3600
    settings_slope = {'slope_min':        0.01,                  # minimum slope to trial
                      'slope_max':        0.2,                    # maximum slope to trial
                      'delta_slope':      0.005,                  # slope increment
                      'date_range':       [1999,2020],            # range of dates over which to perform the analysis
                      'n_days':           8,                      # sampling period [days]
                      'n0':               50,                     # parameter for Nyquist criterium in Lomb-Scargle transforms
                      'freqs_cutoff':     1./(seconds_in_day*30), # 1 month frequency
                      'delta_f':          100*1e-10,              # deltaf for identifying peak tidal frequency band
                      'prc_conf':         0.05,                   # percentage above minimum to define confidence bands in energy curve
                      }
    settings_slope['date_range'] = [pytz.utc.localize(datetime(settings_slope['date_range'][0],5,1)),
                                    pytz.utc.localize(datetime(settings_slope['date_range'][1],1,1))]
    beach_slopes = SDS_slope.range_slopes(settings_slope['slope_min'], settings_slope['slope_max'], settings_slope['delta_slope'])

    t = np.array([_.timestamp() for _ in df.index]).astype('float64')
    delta_t = np.diff(t)
    fig, ax = plt.subplots(1,1,figsize=(12,3), tight_layout=True)
    ax.grid(which='major', linestyle=':', color='0.5')
    bins = np.arange(np.min(delta_t)/seconds_in_day, np.max(delta_t)/seconds_in_day+1,1)-0.5
    ax.hist(delta_t/seconds_in_day, bins=bins, ec='k', width=1);
    ax.set(xlabel='timestep [days]', ylabel='counts',
          xticks=7*np.arange(0,20),
          xlim=[0,50], title='Timestep distribution');

    # find tidal peak frequency (can choose 7 or 8 in this case)
    settings_slope['n_days'] = 7
    settings_slope['freqs_max'] = SDS_slope.find_tide_peak(df.index,tides.tide,settings_slope)
    # estimate beach-face slopes along the transects
    slope_est, cis = dict([]), dict([])
    for key in df.keys():
        # remove NaNs
        idx_nan = np.isnan(df[key])
        dates = [df.index[_] for _ in np.where(~idx_nan)[0]]
        tide = tides.tide.to_numpy()[~idx_nan]
        composite = df[key][~idx_nan]
        # apply tidal correction
        tsall = SDS_slope.tide_correct(composite,tide,beach_slopes)
        title = 'Transect %s'%key
        SDS_slope.plot_spectrum_all(dates,composite,tsall,settings_slope, title)
        slope_est[key],cis[key] = SDS_slope.integrate_power_spectrum(dates,tsall,settings_slope)
        print('Beach slope at transect %s: %.3f'%(key, slope_est[key]))
    transects.beach_slope.update(slope_est)
    transects.cil.update({k: v[0] for k,v in cis.items()})
    transects.ciu.update({k: v[1] for k,v in cis.items()})
    transects[transects.index.isin(slope_est.keys())]
  transects.to_file("transects_extended.geojson")