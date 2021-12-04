import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import re
import pickle


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def list_files(directory="data", extension=".xls"):
    lst = []
    for file in os.listdir(directory):
        if file.endswith(extension):
            lst.append(os.path.join(directory, file))
    return sorted(lst)


def clean_headers(data, time_column='Tid'):
    # Change column headers
    new_columns = [''] * len(data.columns)  # data.columns[0]
    new_columns[0] = time_column
    for i in range(1, len(data.columns)):
        cleaned_column = re.sub('\.[0-9]+$|\ ', '', data.columns[i])
        new_columns[i] = ' '.join(np.append(cleaned_column, data.iloc[:2, i]))
    data.columns = new_columns

    # Drop Unnamed columns
    for column in data.columns:
        if 'Unnamed' in column:
            # data.drop(data.index[[0, 1, 2, 3]], inplace=True)
            data.drop(columns=[column], inplace=True)

    # Drop headers
    data.drop(data.index[[0, 1, 2, 3]], inplace=True)
    data.reset_index(drop=True, inplace=True)

    # Fix incorrect time formats
    data[time_column] = parse_dates(data[time_column])


def try_parsing_date(text):
    for fmt in ('%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


def parse_dates(dates):
    parsed = len(dates)*['']
    for i in range(len(dates)):
        if type(dates[i]) is str:
            parsed[i] = try_parsing_date(dates[i])
        elif type(dates[i]) is np.int64:
            parsed[i] = datetime.strptime(str(dates[i]), '%Y')
        else:
            parsed[i] = dates[i]
    return parsed


def import_raw_data(dir="data/raw", format=".xls"):
    try:
        return pd.read_pickle(os.path.join(dir, 'data.pkl'))
    except FileNotFoundError:
        files = list_files(dir, format)
        data = None
        for file in files:
            print("Importing data from: %s" %file)
            new_data = pd.read_excel(file)
            clean_headers(new_data)

            if data is None:
                data = new_data.copy()
            else:
                data = pd.concat([data, new_data], ignore_index=True)

        # Save data to file
        data.to_pickle(os.path.join(dir, 'data.pkl'))
        return data


def calc_power_totals(data, time_column='Tid'):
    words = ['SE1', 'SE2', 'SE3', 'SE4']
    totals = pd.DataFrame(data, columns=[time_column])
    for column in data.columns:
        if any(word in column for word in words):
            try:
                totals[column[:-4]] += data[column].fillna(0)
            except KeyError:
                totals[column[:-4]] = data[column].fillna(0)

    # Remove strange '----' strings
    to_clean = ['Ospec. förbrukning', 'Gast./diesel produktion']
    for column in to_clean:
        clean_column = len(totals[column])*[0]
        for i in range(len(clean_column)):
            if type(totals[column][i]) is str:
                clean_column[i] = 0
            else:
                clean_column[i] = totals[column][i]
        totals[column] = clean_column

    return totals


def import_installed_power_data(directory="data/installed", extension=".xlsx", time_column='Tid'):
    file = list_files(directory, extension)[0]
    data = pd.read_excel(file)
    data[time_column] = parse_dates(data[time_column]+1)
    return data


def to_numpy(panda):
    data = {}
    for column in panda.columns:
        data[column] = panda[column].to_numpy()
    return data  # dotdict(data)


def calc_averages(data, freq='d', time_key='Tid', normalize=True):
    if freq == 'm':
        freq = 'MS'
    if freq == 'y':
        freq = 'YS'
    start_date = np.min(data[time_key])
    end_date = np.max(data[time_key])
    date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
    next_date = pd.DatetimeIndex([date_range[-1]+1*date_range.freq])
    date_range = date_range.append(next_date)
    # Create a new data set and add the new dates vector
    new_data = {time_key: date_range[:-1]}
    n = len(date_range)
    for key in data.keys():
        if key != time_key:
            new_data[key] = np.zeros(shape=n-1)
            for i in range(n-1):
                mask = (date_range[i] <= data[time_key]) * (data[time_key] < date_range[i+1])
                if normalize is True:
                    new_data[key][i] = np.mean(data[key][mask])
                else:
                    new_data[key][i] = np.sum(data[key][mask])
    return new_data


def time_data(data, time_key='Tid'):
    n = len(data[time_key])
    hour = np.zeros(shape=n)
    day = np.zeros(shape=n)
    month = np.zeros(shape=n)
    year = np.zeros(shape=n)
    weekday = np.zeros(shape=n)
    for i in range(n):
        hour[i] = pd.Timestamp(data[time_key][i]).hour
        day[i] = pd.Timestamp(data[time_key][i]).day
        month[i] = pd.Timestamp(data[time_key][i]).month
        year[i] = pd.Timestamp(data[time_key][i]).year
        weekday[i] = pd.Timestamp(data[time_key][i]).weekday()
    data['hour'] = hour
    data['day'] = day
    data['month'] = month
    data['year'] = year
    data['weekday'] = weekday


def interp(data, data0, time_key='Tid'):
    epoch = np.datetime64('1970-01-01T00:00:00Z')
    t = np.asarray([(d - epoch).astype("float") for d in data[time_key]])
    t0 = np.asarray([(d - epoch).astype("float") for d in data0[time_key]])
    for key in data0.keys():
        if key != time_key:
            data[key] = np.interp(t, t0, data0[key])
            # f = interp1d(t0, data0[key], kind='cubic',fill_value="extrapolate")
            # data[key] = f(t)


def import_data(data_name='hourly'):
    try:
        with open('data/data.pkl', 'rb') as file:
            data = pickle.load(file)
    except FileNotFoundError:
        raw_data = import_raw_data()
        installed_power = import_installed_power_data()
        power_totals = calc_power_totals(raw_data)

        data = {'raw': to_numpy(raw_data),
                'installed': to_numpy(installed_power),
                data_name: to_numpy(power_totals)}

        # Calculate daily and yearly averages and sums
        data['daily'] = calc_averages(data[data_name], freq='d', normalize=True)
        data['monthly'] = calc_averages(data[data_name], freq='m', normalize=True)
        data['yearly'] = calc_averages(data[data_name], freq='y', normalize=True)
        data['daily_sum'] = calc_averages(data[data_name], freq='d', normalize=False)
        data['monthly_sum'] = calc_averages(data[data_name], freq='m', normalize=False)
        data['yearly_sum'] = calc_averages(data[data_name], freq='y', normalize=False)

        # Add installed power to hourly data
        interp(data['hourly'], data['installed'])

        # Add vectors signifying hour, day, month, year and weekday
        time_data(data[data_name])

        # Save as binary file
        with open('data/data.pkl', 'wb') as file:
            pickle.dump(data, file)
    return dotdict(data)

