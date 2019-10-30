#%%
import numpy as np
import pandas as pd
import datetime
import time
import copy
import pickle
import sys
import argparse
from multiprocessing import Process, Pool
# from ftp import FTP, FTUP

from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import MinMaxScaler

import warnings
warnings.filterwarnings("ignore")

def test_this():
    return 'test_succeed'

# Helpers
def save_dataset(dataset, filename):
    """Save dataset"""
    pickle.dump(dataset, open(filename, 'wb'))


def load_dataset(filename):
    """Load dataset"""
    with open(filename, 'rb') as f:
        return pickle.load(f)


# Data
class Data():

    def __init__(self,):
        """Just init"""
        pass


    def read_csv(self, filename='./data/sales2.csv', sep=',', header=0 ):
        """Load data and preprocess"""
        df = pd.read_csv(filename, sep=sep, header=header)
        self.set_ds_index(df)
        self.get_groups()
        self.outbound = self.outbound_interface(df.index[0], 36, 12)
        return self.df


    def set_ds_index(self, df):
        """Create date index"""
        df.columns = ['style', 'color', 'size', 'division', 'category', 'subcat','subgroup','year','month','qty']
        dateparse = lambda dates: pd.datetime.strptime(dates, '%Y-%m-%d %H:%M:%S')
        date_index = [dateparse(f'{df.year[i]}-{df.month[i]}-1 00:00:00') for i in df.index]
        df.index = date_index
        self.df = df


    def get_groups(self,):
        """Create (sub)group lists"""
        style_map = self.df.groupby(['style', 'division', 'category', 'subgroup']).size()
        style_map = style_map.reset_index()

        self.divisions = style_map['division'].sort_values().unique().astype(int)
        self.categories = style_map['category'].sort_values().unique().astype(int)
        self.subgroups = style_map['subgroup'].sort_values().unique().astype(int)
        self.styles = style_map['style'].sort_values().unique().astype(int)


    def outbound_interface(self, start_date, window=36, horizon=12, freq='M'):
        """Outbound interface for each time serie"""
        start_date = str(start_date)
        periods = window + horizon
        dateparse = lambda dates: pd.datetime.strptime(dates, '%Y-%m-%d %H:%M:%S')
        df = pd.DataFrame()

        # Columns for setup and possibly merging forecast
        df['timestamp'] = pd.date_range(dateparse(start_date), periods=periods, freq=freq).tolist()
        df['ds'] = pd.date_range(dateparse(start_date), periods=periods, freq=freq).date.tolist()

        # Outbound interface columns
        df['style'] = None
        df['color'] = 1
        df['size'] = 1
        df['year'] = pd.date_range(dateparse(start_date), periods=periods, freq=freq).year.tolist()
        df['month'] = pd.date_range(dateparse(start_date), periods=periods, freq=freq).month.tolist()
        df['qty'] = 0

        # Remove setup columns
        df = df.loc[:, ['timestamp', 'style','color','size','year','month','qty']]
        return df.set_index('timestamp')

    def get_outbound(self,):
        """Return outbound interface"""
        return self.outbound


# HW
class HoltWinters:
    """Holt-Winters model with the anomalies detection using Brutlag method

    # series - initial time series
    # slen - length of a season
    # alpha, beta, gamma - Holt-Winters model coefficients
    # n_preds - predictions horizon
    # window - validation window
    # scaling_factor - sets the width of the confidence interval by Brutlag (usually takes values from 2 to 3)"""

    def __init__(self, series, slen, alpha, beta, gamma, n_preds=12, window=12, scaling_factor=1.96):
        assert len(series) / slen >= 2, f'seasonal length must be max half size of time series'
        self.window = window
        self.series_ = self.clip(series).astype(np.int32)
        self.series = self.series_
        if self.window > 0:
            self.series = self.clip(series[:-window]).astype(np.int32)
            self.valid = self.clip(series[-window:]).astype(np.int32)
        self.slen = slen #
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.n_preds = n_preds
        self.scaling_factor = scaling_factor


    def clip(self, series):
        """Helper to clip values between 0 and infinity and set NaN to zero"""
        series = np.nan_to_num(series)
        series[series<0] = 0
        return series # TODO np.clip(series, 0, np.inf)


    def exp_relu(self, value, prev_value=0, param=1):
        """Helper to clip a value between 0 and infinity and set NaN to zero"""
        return max(0., param*value + (1-param)*prev_value)


    def initial_trend(self, sum_=0.):
        N = self.series.size//2
        return np.mean([float(self.series[i+N] - self.series[i]) / N for i in range(N)])


    def initial_seasonal_components(self):
        seasonals = {}
        season_averages = []
        n_seasons = int(len(self.series)/self.slen)
        # Averages by season
        for j in range(n_seasons):
            season_averages.append(np.sum(self.series[self.slen*j:self.slen*j+self.slen])/float(self.slen))

        # Initial seasonal values by lag - adjusted with seasonal average
        for i in range(self.slen):
            sum_of_vals_over_avg = 0.
            for j in range(n_seasons):
                sum_of_vals_over_avg += self.series[self.slen*j+i]-season_averages[j]
            seasonals[i] = sum_of_vals_over_avg/n_seasons
        return seasonals


    def fit(self):
        """Triple Exponential Smoothing with
        Guided Walk Forward prediction"""
        self.result = []
        self.Smooth = []
        self.Trend = []
        self.Season = []
        self.PredictedDeviation = []
        seasonals = self.initial_seasonal_components()

        for i in range(len(self.series)+self.n_preds):
            if i == 0:                                   # components initialization
                smooth = self.series[0]
                trend = self.initial_trend()
                self.result.append(self.series[0])
                self.Smooth.append(smooth)
                self.Trend.append(trend)
                self.Season.append(seasonals[i%self.slen])
                self.PredictedDeviation.append(0)

            elif i >= len(self.series):
                # Guided Walk Forward prediction - use last season value + last results as last value
                val = self.exp_relu(self.result[-1], self.series[i-self.n_preds], self.alpha)
                last_smooth, smooth = smooth, self.exp_relu(val-seasonals[i%self.slen], smooth+trend, self.alpha)
                trend = self.exp_relu(self.Trend[-self.n_preds + i])
                seasonals[i%self.slen] = self.exp_relu(val-smooth, seasonals[i%self.slen], self.gamma)
                self.result.append(smooth+trend+seasonals[i%self.slen])

            else:
                # fitting phase
                val = self.series[i]
                last_smooth, smooth = smooth, self.exp_relu(val-seasonals[i%self.slen], smooth+trend, self.alpha)
                trend = self.exp_relu(smooth-last_smooth, trend, self.beta)
                seasonals[i%self.slen] = self.exp_relu(val-smooth, seasonals[i%self.slen], self.gamma)
                self.result.append(smooth+trend+seasonals[i%self.slen])

            self.Smooth.append(smooth)
            self.Trend.append(trend)
            self.Season.append(seasonals[i%self.slen])


    def mape(self, y_true, y_pred, eps=1.):
        """MAPE metric with divide by zero correction"""
        M = (y_true==0)
        y_true = y_true[:].astype(float)
        y_true[M] = eps
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


    def accuracy(self,):
        """Accuracy metrics"""
        if self.window > 0:
            fit = self.result[-self.window:]
            mape = self.mape(self.valid, fit)
        else:
            fit = self.result[:len(self.series)]
            mape = self.mape(self.series, fit)
        return mape


# HW CV
def CVscore(params, values, slen, loss_function=mean_squared_error, window=0):
    """Returns test error on Holt-Winters Cross Validation
        params - vector of parameters for optimization
        values - dataset with timeseries
        slen - season length for Holt-Winters model
        for CV window is 0"""

    alpha, beta, gamma = params
    errors = []
    i = 0

    # One full season at start and other full seasons from end CV split
    irange = lambda a,b: list(range(a,b))
    timeseries_split = [(irange(i-slen*3, i-slen), irange(i-slen, i)) \
                        for n, i in enumerate(range(slen*3, len(values), slen))][:1] + \
                            [(irange(i-slen*3, i-slen), irange(i-slen, i)) \
                        for n, i in enumerate(range(len(values), slen*3, -slen))][::-1]


    # Iterate over folds, train model on each, forecast and calculate error
    for train, test in timeseries_split: #(values, slen):
        n_test = len(test)
        model = HoltWinters(series=values[train], slen=slen,
                            alpha=alpha, beta=beta, gamma=gamma, n_preds=n_test, window=window)
        model.fit()

        # Weighted error - sqrt or log scale
        i += 1
        error = loss_function(model.result[-n_test:], values[test]) * np.log(i+1)
        errors.append(error)

    return np.mean(np.array(errors))


# FFT
def fft_forecast(x, horizon=12, window=0, n_harmonics=60, beta=4, min_fc=0, max_fc=1):
    """Fast Fourier Transform Forecast"""
    if window > 0:
        x = x[:-window]

    N = x.size

    # Remove linear average seasonal trend in x
    alpha = np.mean([float(x[i+horizon] - x[i]) / horizon for i in range(N-horizon)])
    t = np.arange(0, x.size)
    x_dtrend = x #- alpha * t

    # Transform to frequency domain using windowing
    x_freqdom = np.fft.fft(x_dtrend + np.kaiser(x_dtrend.size, beta))
    f = np.fft.fftfreq(x.size)

    # Forecast
    t = np.arange(0, x.size + horizon)
    cwave = np.zeros(t.size)

    # Rebuild Composite Sine - walking thru all sines
    for i in np.argsort(abs(f))[:n_harmonics*2+1]:
        ampli = np.abs(x_freqdom[i]) / x_freqdom.size
        phase = np.angle(x_freqdom[i])
        cwave += ampli * np.cos(2 * np.pi * f[i] * t + phase)
    cwave += alpha * t

    # Min max
    if min_fc < max_fc:
        scaler = MinMaxScaler((min_fc, max_fc))
        out = scaler.fit_transform(cwave[-N-horizon:].reshape(-1,1)).squeeze()
    else:
        out = cwave[-N-horizon:]
    return np.clip(out, 0, np.inf).astype(int) #np.nan_to_num(out)



# Scaler
def stockout_scaler(y, horizon):
    """Compensate for stockout based on last period before forecast
    Infer maximum sales based on cummulative sales, convergence means stockout
    Fit Polynomial to y - max sales demand
    Fit Polynomial to cumsum of y - max sales possible
    Assumption: max of polynomial is max. cumulative sales forecast"""
    window = len(y) - horizon
    x = np.arange(len(y))

    # Parabolic fit to y - max y
    lin = np.poly1d(np.polyfit(x[:window], y[:window], 2))
    y_lin = lin(x)
    scaler_lin = np.sum(y_lin) / np.sum(y)
    scaler_lin = min(1.05, scaler_lin)

    y_cum = np.cumsum(y[-2*horizon:-horizon])
    x_cum = np.arange(len(y_cum))

    # Parabolic fit to y_cum - max y_cum
    poly = np.poly1d(np.polyfit(x_cum, y_cum, 2))
    y_max_poly = np.max(poly(x))
    scaler_poly = y_max_poly / np.sum(y)

    # Clip fits to max
    scaler = min(scaler_lin, scaler_poly)
    y_sc = np.r_[y[:-horizon], y[-horizon:] * scaler]
    return y_sc


# Forecast
class Model():
    """Forecast on 2 models(HW + FFT) and average forecasts"""

    def __init__(self, filename='./data/sales2.csv', sep=',', header=0, filename_out='./data/sales2_pred.csv'):
        # Load data
        data = Data()
        self.inbound = data.read_csv(filename=filename, sep=sep, header=header)
        self.outbound = data.get_outbound()
        self.outbound_file = filename_out
        self.group = 'style'
        self.groups = data.styles
        self.ts = self.inbound.pivot_table(values='qty',
                                 aggfunc=np.sum,
                                 index=self.group,
                                 columns=self.inbound.index).fillna(0)


    def timeseries(self, group_id):
        """TS"""
        ts = self.ts.loc[group_id].values
        ts_ma = copy.deepcopy(pd.Series(ts).ewm(com=.2).mean().values.astype(np.int32))
        return ts, ts_ma[:-self.horizon] # TODO cut window


    def predict(self, window=0, horizon=12, slen=6):
        """Mulitprocess prediction and save results as df and outbound interface"""

        self.window = window
        self.horizon = horizon
        self.slen = slen
        print(f'Forecasting {horizon} periods... ', end="", flush=True)

        # Parallel processing on 4 processors/cores - BorkenPipeError
        with Pool(4) as p:
            self.preds_df = pd.DataFrame(p.map(self._predict, self.groups),
                                         columns=['group_id', 'data', 'prediction', 'RMSE'])

        #### TODO return csv or json
        # return self.preds_df.to_csv(index=False)
        return self.preds_df.to_json(orient='index')

        ####### TODO - reimplement??
        # Save model data and outbound interface
#         self.save_df()
        # message = self.save_forecast()
        # print(f'forecasts saved.')

        # Upload to FTP server
        # FTP(self.outbound_file)
        # FTP(url_for('uploaded_file', filename=self.outbound_file))
        # message = FTUP(self.outbound_file, 'upload')
        # return message

    def _predict(self, group_id):
        """Predict models
        Zero forecast of items with less than 2 periods sales in last 6 periods
        TODO: develop alternative to zero forecast: KNN?
        Validation: window = 12
        Forecast:   window = 0"""

        # Min n months of sales in last half year
        min_sales_threshold = 2
        last_period = 6

        # Timeseries
        ts, X = self.timeseries(group_id)

        if np.sum(X[-last_period:] > 0) > min_sales_threshold:

            # FFT Fit and predict
            fc_fft = fft_forecast(X, self.horizon, self.window, beta=0, min_fc=np.min(X[-12:]), max_fc=np.max(X[-12:]))

            # HW Fit and predict
            margin = (.025, .975)
            opt = minimize(CVscore, x0=[.95, .2, .4],
                           args=(X, self.slen, mean_squared_error),
                           method='L-BFGS-B', bounds=(margin, margin, margin))
            alpha, beta, gamma = opt.x
            model = HoltWinters(X, slen=self.slen,
                                alpha=alpha, beta=beta, gamma=gamma,
                                n_preds=self.horizon,
                                window=self.window,
                                scaling_factor=1.96)
            model.fit()
            fc_hw = np.array(model.result[-self.horizon:])

            # Average predictions
            alpha = .65
            fc_ = (alpha * fc_fft[-self.horizon:] + (1-alpha) * fc_hw.squeeze())
            rmse = np.mean((fc_ - ts[-self.horizon:])**2)**.5
        else:
            rmse = 0
            fc_ = np.ones_like(ts[-self.horizon:])

        # TODO
        fc_scaled = stockout_scaler(np.r_[ts, fc_], self.horizon)

        return (group_id.astype(int), ts, fc_scaled[-self.horizon:], rmse)


    def save_forecast(self,):
        """Concat all styles into one outbound interface"""
        ttl_outbound = pd.DataFrame()
        for i in self.preds_df.index:
            self.outbound['style'] = self.preds_df.loc[i, 'group_id']
            # self.outbound['qty'] = np.r_[self.preds_df.loc[i, 'data'], self.preds_df.loc[i, 'prediction']].astype(int)
            self.outbound['qty'] = np.concatenate((self.preds_df.loc[i, 'data'], self.preds_df.loc[i, 'prediction']), axis=None).astype(int)
            ttl_outbound = pd.concat([ttl_outbound, self.outbound])
        # Fix/clip invalid values
        fix = lambda x: np.clip(np.nan_to_num(x), 0, 99e6).astype(int)
        ttl_outbound['qty'] = fix(ttl_outbound['qty'])
        ttl_outbound.to_csv(self.outbound_file) # f'outbound_interface_{self.window}_.csv'
        return 'holymoly'


    def save_df(self,):
        """Save/pickle df"""
        self.preds_df['RMSE'] = pd.to_numeric(self.preds_df['RMSE'])
        self.preds_df['group_id'] = pd.to_numeric(self.preds_df['group_id']).astype(int)
        save_dataset(self.preds_df, f'styles_predictions_preds_df_{self.window}_.pkl')

