import numpy as np
import sesd
#
# import statsmodels.api as sm
ts = np.random.random(100)
# Introduce artificial anomalies
ts[14] = 9
ts[83] = 10
outliers_indices = sesd.seasonal_esd(ts, periodicity=20, hybrid=True, max_anomalies=2)
for idx in outliers_indices:
    print("Anomaly index: " + idx + " anomaly value: " + ts[idx])