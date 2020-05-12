import os
import pandas as pd
tucson_rain = pd.read_csv(r"/Users/jennahonan/PycharmProjects/502/data/tucson_rain.txt", sep='\t')  #please use relative path rather than absolute path to improve reproducibility
flagstaff_rain = pd.read_csv(r"/Users/jennahonan/PycharmProjects/502/data/flagstaff_rain.txt", sep='\t')

tucson_rain2 = tucson_rain['quality'] == 'Good'
tucson_rain = tucson_rain[tucson_rain2]
flagstaff_rain2 = flagstaff_rain['quality'] == 'Good'
flagstaff_rain = flagstaff_rain[flagstaff_rain2]

dates_tucson = tucson_rain['readingDate'].str.split('-')
tucson_rain['year']=[dates_tucson[i][0] for i in dates_tucson.index]
tucson_rain['month']=[dates_tucson[i][1] for i in dates_tucson.index]
tucson_rain['day']=[dates_tucson[i][2] for i in dates_tucson.index]
dates_flagstaff = flagstaff_rain['readingDate'].str.split('-')
flagstaff_rain['year']=[dates_flagstaff[i][0] for i in dates_flagstaff.index]
flagstaff_rain['month']=[dates_flagstaff[i][1] for i in dates_flagstaff.index]
flagstaff_rain['day']=[dates_flagstaff[i][2] for i in dates_flagstaff.index]
tucson_rain.groupby(["year","month"],axis=0,as_index=True).sum().index.get_level_values(1).tolist()

flagstaff_rain.groupby(["year","month"],axis=0,as_index=True).sum().index.get_level_values(1).tolist()

tucson_rain.groupby(["year","month"],axis=0,as_index=True).sum().index.get_level_values(0).tolist()

flagstaff_rain.groupby(["year","month"],axis=0,as_index=True).sum().index.get_level_values(0).tolist()

rain_sum_tucson=tucson_rain.groupby(["year","month"],axis=0,as_index=True).sum()
rain_sum_flagstaff=flagstaff_rain.groupby(["year","month"],axis=0,as_index=True).sum()

df_tucson_year=tucson_rain.groupby(["year","month"],axis=0,as_index=True).sum().index.get_level_values(0).tolist()
df_tucson_month=tucson_rain.groupby(["year","month"],axis=0,as_index=True).sum().index.get_level_values(1).tolist()
df_tucson_rain=rain_sum_tucson['rainAmount'].tolist()
df_flagstaff_year=flagstaff_rain.groupby(["year","month"],axis=0,as_index=True).sum().index.get_level_values(0).tolist()
df_flagstaff_month=flagstaff_rain.groupby(["year","month"],axis=0,as_index=True).sum().index.get_level_values(1).tolist()
df_flagstaff_rain=rain_sum_flagstaff['rainAmount'].tolist()

df_tucson=pd.DataFrame({'year':df_tucson_year, 'month':df_tucson_month, 'tucson rain':df_tucson_rain})
df_flagstaff=pd.DataFrame({'flagstaff year':df_flagstaff_year, 'flagstaff month':df_flagstaff_month, 'flagstaff rain':df_flagstaff_rain})

df_tucson.insert(3, "flagstaff rain", df_flagstaff_rain)

df_tucson["difference"]=df_tucson["tucson rain"] - df_tucson["flagstaff rain"]

df_tucson.to_csv(r"/Users/jennahonan/PycharmProjects/502/data/rain_difference_2015_2020_version2.txt", header=None, index=None, sep='\t', mode='a')

from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

rain_glm_tucson=smf.glm(formula="df_tucson_rain~month+year",data=df_tucson, family=sm.families.Gaussian())
rain_glm_flagstaff=smf.glm(formula="df_flagstaff_rain~month+year",data=df_tucson, family=sm.families.Gaussian())
res_tucson=rain_glm_tucson.fit()
res_flagstaff=rain_glm_flagstaff.fit()

res_flagstaff.summary()
<class 'statsmodels.iolib.summary.Summary'>
"""
                 Generalized Linear Model Regression Results                  
==============================================================================
Dep. Variable:      df_flagstaff_rain   No. Observations:                   61
Model:                            GLM   Df Residuals:                       44
Model Family:                Gaussian   Df Model:                           16
Link Function:               identity   Scale:                          141.53
Method:                          IRLS   Log-Likelihood:                -227.64
Date:                Sun, 10 May 2020   Deviance:                       6227.2
Time:                        17:53:42   Pearson chi2:                 6.23e+03
No. Iterations:                     3                                         
Covariance Type:            nonrobust                                         
================================================================================
                   coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------
Intercept       11.3956      6.143      1.855      0.064      -0.645      23.436
month[T.02]     -0.4590      7.524     -0.061      0.951     -15.206      14.288
month[T.03]     -1.6480      7.524     -0.219      0.827     -16.395      13.099
month[T.04]     -1.4220      7.524     -0.189      0.850     -16.169      13.325
month[T.05]      5.5820      7.524      0.742      0.458      -9.165      20.329
month[T.06]      4.2660      7.524      0.567      0.571     -10.481      19.013
month[T.07]     23.9780      7.524      3.187      0.001       9.231      38.725
month[T.08]     32.3010      7.524      4.293      0.000      17.554      47.048
month[T.09]      6.3630      7.524      0.846      0.398      -8.384      21.110
month[T.10]     12.3860      7.524      1.646      0.100      -2.361      27.133
month[T.11]      2.3100      7.524      0.307      0.759     -12.437      17.057
month[T.12]      0.4760      7.524      0.063      0.950     -14.271      15.223
year[T.2016]    -2.2808      4.857     -0.470      0.639     -11.800       7.238
year[T.2017]   -10.5954      4.857     -2.182      0.029     -20.114      -1.076
year[T.2018]    -6.9767      4.857     -1.436      0.151     -16.496       2.542
year[T.2019]    -8.3550      4.857     -1.720      0.085     -17.874       1.164
year[T.2020]   -11.3956     13.389     -0.851      0.395     -37.638      14.847
================================================================================
"""

res_tucson.summary()
<class 'statsmodels.iolib.summary.Summary'>
"""
                 Generalized Linear Model Regression Results                  
==============================================================================
Dep. Variable:         df_tucson_rain   No. Observations:                   61
Model:                            GLM   Df Residuals:                       44
Model Family:                Gaussian   Df Model:                           16
Link Function:               identity   Scale:                      1.4061e+05
Method:                          IRLS   Log-Likelihood:                -438.13
Date:                Sun, 10 May 2020   Deviance:                   6.1869e+06
Time:                        17:54:24   Pearson chi2:                 6.19e+06
No. Iterations:                     3                                         
Covariance Type:            nonrobust                                         
================================================================================
                   coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------
Intercept      614.7832    193.640      3.175      0.001     235.257     994.310
month[T.02]   -111.1682    237.159     -0.469      0.639    -575.991     353.655
month[T.03]   -473.5237    237.159     -1.997      0.046    -938.347      -8.700
month[T.04]   -510.6857    237.159     -2.153      0.031    -975.509     -45.862
month[T.05]   -527.6446    237.159     -2.225      0.026    -992.468     -62.821
month[T.06]   -347.3220    237.159     -1.465      0.143    -812.145     117.501
month[T.07]    268.1739    237.159      1.131      0.258    -196.649     732.997
month[T.08]    244.6167    237.159      1.031      0.302    -220.207     709.440
month[T.09]     39.6268    237.159      0.167      0.867    -425.197     504.450
month[T.10]    -94.3320    237.159     -0.398      0.691    -559.155     370.491
month[T.11]   -290.1422    237.159     -1.223      0.221    -754.966     174.681
month[T.12]   -167.2191    237.159     -0.705      0.481    -632.042     297.604
year[T.2016]   -33.4488    153.086     -0.218      0.827    -333.491     266.593
year[T.2017]  -154.4385    153.086     -1.009      0.313    -454.481     145.604
year[T.2018]    -1.8718    153.086     -0.012      0.990    -301.914     298.170
year[T.2019]    44.1702    153.086      0.289      0.773    -255.872     344.212
year[T.2020]  -614.7432    422.028     -1.457      0.145   -1441.902     212.416
================================================================================
"""
