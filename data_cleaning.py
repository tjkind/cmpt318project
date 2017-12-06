import pandas as pd
import numpy as np
import numpy.polynomial.polynomial as poly
import matplotlib.pyplot as plt
import statsmodels.nonparametric.smoothers_lowess as st
from pykalman import KalmanFilter
from scipy import signal
import re
#import warnings
np.warnings.filterwarnings('ignore')


in_filename = "raw_accel.csv"
out_filename = "move_polys.csv"
col_names = ["move", "x", "y", "z", "time", "err1",  "err2",  "err3"]
name_equiv = {'s': 'standing', 't':'tendu', 'j':'saute', 'r': 'retire', 'a': 'assemble'}

def check_len(m):
    return len(m['x']) > 70

def rename(m):
    match = re.search(r'([a-z]+)', m)
    match = match.group(1)
    string = name_equiv[match]
    return string

def smoothing(m):
    #not used as it did not improve performance, left for referance only
    b, a = signal.butter(3, 0.01, btype='lowpass', analog=False)
    low_x = signal.filtfilt(b, a, m['x'])
    low_y = signal.filtfilt(b, a, m['y'])
    low_z = signal.filtfilt(b, a, m['z'])
    m['x'] = low_x
    m['y'] = low_y
    m['z'] = low_z
    if(np.isnan(m['x']).any() | np.isnan(m['y']).any() | np.isnan(m['x']).any()):
        m['move'] = None 
        return 
    return m

def polyfitting(m):
    coef_x = poly.polyfit(m['time'], m['x'], 3)
    coef_y = poly.polyfit(m['time'], m['y'], 3)
    coef_z = poly.polyfit(m['time'], m['z'], 3)
    return m['move'], coef_x, coef_y, coef_z

def plot_graph(df, n):
    #plots the x, y, z changes of particualr move
    m = df.iloc[n]
    print(m)
    x = m['time']
    yx = m['x']
    yy = m['y']
    yz = m['z']
    plt.subplot(3, 1, 1)
    plt.plot(x, yx)
    plt.subplot(3, 1, 2)
    plt.plot(x, yy)
    plt.subplot(3, 1, 3)
    plt.plot(x, yz)
    plt.show

def clean_data(in_filename, out_filename, plot):
    moves_raw = pd.read_csv(in_filename, names = col_names)
    moves_raw = moves_raw[pd.isnull(moves_raw['err1'])]
    moves_raw = moves_raw.drop(["err1",  "err2",  "err3"], axis =1)
    moves_raw = moves_raw.dropna(how = 'any')
    
    moves_raw['x'] = pd.to_numeric(moves_raw['x'], errors='coerce')
    moves_raw['y'] = pd.to_numeric(moves_raw['y'], errors='coerce')
    moves_raw['z'] = pd.to_numeric(moves_raw['z'], errors='coerce')
    moves_raw['time'] = pd.to_numeric(moves_raw['time'], errors='coerce')
    
    grouped_moves = moves_raw.groupby('move')
    moves = pd.DataFrame(grouped_moves.apply(lambda x: np.sort(x['x'].as_matrix())))
    moves = moves.rename(index=str, columns={0:'x'}).reset_index()

    temp = pd.DataFrame(grouped_moves.apply(lambda x: np.sort(x['y'].as_matrix())))
    temp = temp.rename(index=str, columns={0:'y'}).reset_index()
    moves = moves.merge(temp, on='move')
    
    temp = pd.DataFrame(grouped_moves.apply(lambda x: np.sort(x['z'].as_matrix())))
    temp = temp.rename(index=str, columns={0:'z'}).reset_index()
    moves = moves.merge(temp, on='move')
    
    temp = pd.DataFrame(grouped_moves.apply(lambda x: np.sort(x['time'].as_matrix())))
    temp = temp.rename(index=str, columns={0:'time'}).reset_index()
    moves = moves.merge(temp, on='move')
    
    moves = moves[moves.apply(check_len, axis=1)]
    
    moves['move'] = moves['move'].apply(rename)    
#    moves = moves.apply(smoothing, axis=1)
    moves = moves.dropna(how = 'any')
    
    if(plot is not None):
        plot_graph(moves, plot)
    
    moves_coeffs = pd.DataFrame(moves.apply(polyfitting, axis=1), columns = ['conglomerated'])
    
    moves_coeffs = pd.DataFrame(moves_coeffs['conglomerated'].values.tolist(), columns = ['move', 'x', 'y', 'z'])
    moves_coeffs[['x3', 'x2', 'x1', 'x0']] = pd.DataFrame(moves_coeffs['x'].values.tolist())
    moves_coeffs[['y3', 'y2', 'y1', 'y0']] = pd.DataFrame(moves_coeffs['y'].values.tolist())
    moves_coeffs[['z3', 'z2', 'z1', 'z0']] = pd.DataFrame(moves_coeffs['z'].values.tolist())
    moves_coeffs = moves_coeffs.drop(['x', 'y', 'z'], axis = 1)
    moves_coeffs = moves_coeffs.dropna(how = 'any') 

    if(out_filename is not None):
        moves_coeffs.to_csv(out_filename)

    return moves_coeffs