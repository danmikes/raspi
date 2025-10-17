#!/usr/bin/env python
# coding: utf-8

# SamSim

# Import

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import time
import warnings
from collections import ChainMap, namedtuple
from IPython.display import clear_output
from itertools import product
from matplotlib.table import Table
from scipy.optimize import curve_fit

warnings.filterwarnings('ignore', category=RuntimeWarning)

plt.style.use('dark_background')

DARK_COLORS = {
  'red': '#ff6b6b',
  'green': '#51cf66',
  'yellow': '#ffd43b', 
  'cyan': '#22b8cf',
  'magenta': '#cc5de8',
  'darkcyan': '#20c997',
  'darkmagenta': '#be4bdb',
  'white': '#f8f9fa',
  'grid': '#495057',
  'background': '#212529'
}

# Parameter

def form(val):
  if val >= 1e3:
    return f'{val:.2e}'
  elif val.is_integer():
    return f'{val:.0f}'
  else:
    return f'{val:.2f}'

def print_params(params):
  for param, values in params.items():
    formatted_values = [
      form(val) for val in values
    ]
    print(f'{param}: {formatted_values}')

# Period Ma
_T1 = int(1.0e5)
_T2 = int(4.1e4)
_T3 = int(2.6e4)

# Amplitude -
_A1 = int(2)
_A2 = int(25)
_A3 = int(15)

# Period modulation Ma
_Tm1 = int(_T1 * 5)
_Tm2 = int(_T2 * 5)
_Tm3 = int(_T3 * 5)

# Amplitude modulation -
_Am1 = int(_A1 / 2)
_Am2 = int(_A2 / 2)
_Am3 = int(_A3 / 2)

# Phase radian
_p1 = int(0)
_p2 = int(0)
_p3 = int(0)

# Other
DUR = int(1e6) # duration Ma
SIG = int(1e3) # signal-rate
SAM = int(1e2) # sample-rate
REP = int(1e1) # repeat

Par = namedtuple('Pars', ['T', 'A', 'Tm', 'Am', 'p'])
PAR1 = Par(_T1, _A1, _Tm1, _Am1, 0)
PAR2 = Par(_T2, _A2, _Tm2, _Am2, 0)
PAR3 = Par(_T3, _A3, _Tm3, _Am3, 0)
PARS = PAR1, PAR2, PAR3

print(PARS)
print(SAM)


# Range

_SAM_SHORT_ = 2 ** np.arange(2, 7, 1)
_SAM_LONG_ = 2 ** np.arange(1, 10, 0.5)

def create_range(prefix, values):
  return {f'{prefix}{i}': np.asarray(values) for i in range(1, 4)}

def ranges(*args):
  return dict(ChainMap(*args))

T = create_range('T', 2. ** np.arange(2, 5) * 1e4)
A = create_range('A', np.arange(0, 26, 5))
Tm = create_range('Tm', 2. ** np.arange(0, 3) * 1e5)
Am = create_range('Am', np.arange(0, 13, 2.5))
p = create_range('p', 2. ** np.arange(-3, -1) * np.pi)

SAM_S = {'sam': _SAM_SHORT_}
SAM_L = {'sam': _SAM_LONG_}

_T_ = ranges(T, SAM_L)
_A_ = ranges(A, SAM_L)
_Tm_ = ranges(Tm, SAM_L)
_Am_ = ranges(Am, SAM_L)
_p_ = ranges(p, SAM_L)
_X_ = ranges(T, A, Tm, Am, SAM_S)
_SAM_S_ = _SAM_SHORT_
_SAM_L_ = _SAM_LONG_

print_params(_A_)


# Scenario

# (edit amplitude) | no modulation
def base(A1=_A1, A2=_A2, A3=_A3):
  return tuple(Par(T, A, 1, 0, 0) for T, A in zip([_T1, _T2, _T3], [A1, A2, A3]))

# (edit amplitude) | default modulation
def fullA(A1=_A1, A2=_A2, A3=_A3):
  return tuple(Par(T, A, Tm, Am, 0) for T, A, Tm, Am in zip([_T1, _T2, _T3], [A1, A2, A3], [_Tm1, _Tm2, _Tm3], [_Am1, _Am2, _Am3]))

# (edit modulation) # Tm Am
def fullM(Tm1=_Tm1, Tm2=_Tm2, Tm3=_Tm3, Am1=_Am1, Am2=_Am2, Am3=_Am3):
  return tuple(Par(T, A, Tm, Am, 0) for T, A, Tm, Am in zip([_T1, _T2, _T3], [_A1, _A2, _A3], [Tm1, Tm2, Tm3], [Am1, Am2, Am3]))

# (edit all) # X
def fullX(T1=_T1, T2=_T2, T3=_T3, A1=_A1, A2=_A2, A3=_A3, Tm1=_Tm1, Tm2=_Tm2, Tm3=_Tm3, Am1=_Am1, Am2=_Am2, Am3=_Am3, p1=_p1, p2=_p2, p3=_p3):
  return tuple(Par(T, A, Tm, Am, p) for T, A, Tm, Am, p in zip([T1, T2, T3], [A1, A2, A3], [Tm1, Tm2, Tm3], [Am1, Am2, Am3], [p1, p2, p3]))

# default all # -
def full():
  return PARS

# Examples
par1 = base()
par2 = base(1, 2, 3)
par3 = fullA()
par4 = fullA(1, 2, 3)
par5 = fullM()
par6 = fullM(1e6, 1e5, 1e4, 1, 2, 3)
par7 = fullX()
par8 = fullX(T1=2e5, A1=8, p1=np.pi/2)

print(par8)


# Insolation

def sine(A, T, t, p=0):
  return A * np.sin(2 * np.pi * 1/T * t + p)

def cosine(Am, Tm, t, p=0):
  return Am * np.cos(2 * np.pi * 1/Tm * t + p)

def run_ins(par1=PAR1, par2=PAR2, par3=PAR3):
  # Generate Time Series
  t = np.linspace(0, DUR, SIG)
  pars = [par1, par2, par3]

  # Modulate Amplitude
  A = [p.A + cosine(p.Am, p.Tm, t) for p in pars]
  signals = [sine(a, p.T, t) for a, p in zip(A, pars)]
  s = sum(signals)

  return t, *signals, s


# Simulation

def cross(signal):
  centered = signal - np.mean(signal)
  return np.sum(np.diff(np.sign(centered)) != 0)

def compare(signal, sample):
  fit = cross(sample) / cross(signal)
  return fit

def run_sim(t, signal, sam=SAM):
  total_fit = 0.0
  # Pre-allocate arrays
  sim_t = np.linspace(0, DUR, sam)
  last_sam_i = last_sam_y = last_sim_x = None
  
  for _ in range(REP):
    sam_i = np.sort(np.random.choice(len(signal), sam, replace=False))
    sam_y = signal[sam_i]
    sim_x = np.interp(t, sim_t, sam_y)
    total_fit += compare(signal, sim_x)
    last_sam_i, last_sam_y, last_sim_x = sam_i, sam_y, sim_x
  
  return t[last_sam_i], last_sam_y, sim_t, last_sim_x, total_fit / REP


# Simulations

def run_sims(t, signal):
  sams = []
  fits = []

  for sam in _SAM_LONG_:
    sam = int(sam)

    # Simulate samples
    _, _, _, _, fit = run_sim(t, signal, sam)

    # Append results
    sams.append(sam)
    fits.append(fit)

  return sams, fits


# Parameters

def run_params(param_ranges):
  sams = []
  fits = []
  param_combinations = product(*param_ranges.values())
  
  # Predefine default values
  defaults = {
    'T1': _T1, 'T2': _T2, 'T3': _T3,
    'A1': _A1, 'A2': _A2, 'A3': _A3,
    'Tm1': _Tm1, 'Tm2': _Tm2, 'Tm3': _Tm3,
    'Am1': _Am1, 'Am2': _Am2, 'Am3': _Am3,
    'p1': _p1, 'p2': _p2, 'p3': _p3,
    'sam': SAM
  }
  
  for combination in param_combinations:
    params = defaults.copy()
    # Update with current combination
    for param, value in zip(param_ranges.keys(), combination):
      params[param] = int(value) if param == 'sam' else value
    
    # Generate signals
    pars = fullX(**{k: params[k] for k in ['T1','T2','T3','A1','A2','A3',
                                          'Tm1','Tm2','Tm3','Am1','Am2','Am3',
                                          'p1','p2','p3']})

    t, _, _, _, signal = run_ins(pars[0], pars[1], pars[2])

    # Simulate samples
    _, _, _, _, fit = run_sim(t, signal, params['sam'])

    # Append results
    sams.append(params['sam'])
    fits.append(fit)

  return sams, fits


# Data

def logistic_function(x, a, b, c):
  return a / (1 + np.exp(-b * (np.log(x) - c)))

def logistic_fit(x_data, y_data, params, maxfev=1e4):
  x_tuple = tuple(x_data)
  y_tuple = tuple(y_data)
  params_tuple = tuple(params)
  return curve_fit(logistic_function, x_tuple, y_tuple, params_tuple, maxfev=int(maxfev))

def find_x_for_y(y, a, b, c):
  x = np.exp(c + np.log(a / (1 / y - 1)) / b)
  return x

def set_plot_prop(ax, x_scale, y_scale, x_title, y_title, title, xlim=None, ylim=None):
  ax.set_facecolor(DARK_COLORS['background'])

  ax.set(
    xscale=x_scale, yscale=y_scale,
    xlabel=x_title, ylabel=y_title,
    title=title,
    xlim=xlim if xlim is not None else ax.get_xlim(),
    ylim=ylim if ylim is not None else ax.get_ylim()
  )
  ax.grid(True, which='both', color='#333', alpha=0.7)

def insolation(fig, pars):
  t, s1, s2, s3, s = run_ins(pars[0], pars[1], pars[2])
  fig.plot(t, s1, color='red', linestyle='-', linewidth=0.6)
  fig.plot(t, s2, color='green', linestyle='-', linewidth=0.6)
  fig.plot(t, s3, color='yellow', linestyle='-', linewidth=0.6)
  fig.plot(t, s, color='cyan')
  set_plot_prop(fig, 'linear', 'linear', 'time [Ma]', 'sea-level [m]', 'Insolation', (0, 1e6))
  return t, s

def simulation(ax, t, signal, sam):
  sam_t, sam_y, sim_t, _, fit = run_sim(t, signal, sam)
  ax.plot(t, signal, color='darkcyan')
  ax.plot(sam_t, sam_y, color='darkmagenta', linestyle='-', linewidth=1, marker='o', markersize='3')
  ax.plot(sim_t, sam_y, color='yellow', marker='o', markersize='3')
  set_plot_prop(ax, 'linear', 'linear', 'time [Ma]', 'sea-level [m]', 'Simulation', (0, 1e6))
  return fit

def simulations(ax, t, signal):
  sams, fits = run_sims(t, signal)
  ax.scatter(sams, fits, s=20, color='darkcyan')
  set_plot_prop(ax, 'log', 'linear', 'samples', 'fit', 'Simulations', (1, 1e3), (0, 1))
  return sams, fits

def parameters(ax, param_ranges):
  sams, fits = run_params(param_ranges)
  ax.scatter(sams, fits, s=5, color='darkcyan')
  set_plot_prop(ax, 'log', 'linear', 'samples', 'fit', 'Parameters', (1, 1e3), (0, 1))
  return sams, fits

def all(ax, param_ranges, title):
  sams, fits = run_params(param_ranges)
  ax.scatter(sams, fits, s=5, color='darkcyan')
  set_plot_prop(ax, 'log', 'linear', 'samples', 'fit', title, (1, 1e3), (0, 1))
  return sams, fits

def logistic(ax, x_data, y_data):
  initial_params = (1, 0.4, 60) # (1.0, 0.4, 60)
  covariance = np.zeros((3, 3))
  fitted_params, covariance = logistic_fit(x_data, y_data, initial_params, 1e5)
  x_fit = np.linspace(min(x_data), max(x_data), 100)
  y_fit = logistic_function(x_fit, fitted_params[0], fitted_params[1], fitted_params[2])
  ax.plot(x_fit, y_fit, color='cyan')
  return fitted_params, covariance


# Table

def display_tab(ax, params):
  y_vals = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
  x_vals = [find_x_for_y(y, *params) for y in y_vals]

  data = [(x, y) for x, y in zip(x_vals, y_vals)][::-1]

  table_data = [['sam', 'fit']] + [[f'{x:.0f}', f'{y:.2f}'] for x, y in data]

  table_x = 0.15
  table_y = -2
  table_w = 0.5
  table_h = 3
  table = Table(ax, bbox=[table_x, table_y, table_w, table_h])
  table.auto_set_font_size(False)
  table.set_fontsize(12)
  table.scale(1, 2)

  for i, row in enumerate(table_data):
    for j, cell in enumerate(row):
      table.add_cell(i, j, width=0.1, height=0.2, text=cell, loc='center', facecolor='black', edgecolor='#333')
  
  table_top = table_y + table_h
  title_y = table_top + 0.1
  title_x = table_x + table_w/2

  ax.add_table(table)
  ax.set_title('Values', fontsize=12, x=title_x, y=title_y)
  ax.axis('off')


# Plot Insolation

def plot_ins(pars=PARS):
  # Figure
  plt.close('all')
  fig, ax = plt.subplots(figsize=(20, 2))

  # Data
  insolation(ax, pars)

  return fig


# Plot Simulation

def plot_sim(sam=SAM, pars=PARS):
  # Figure
  plt.close('all')
  fig, ax = plt.subplots(figsize=(20, 2))

  # Data
  t, _, _, _, signal = run_ins(pars[0], pars[1], pars[2])
  simulation(ax, t, signal, sam)

  return fig


# Plot Simulations

def plot_sims(sam=SAM, param_ranges=_A_, pars=PARS):
  # Figure
  plt.close('all')
  fig = plt.figure(figsize=(20, 6))
  ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3)
  ax2 = plt.subplot2grid((3, 3), (1, 0), rowspan=2)
  ax3 = plt.subplot2grid((3, 3), (1, 1), rowspan=2)
  ax4 = plt.subplot2grid((3, 3), (1, 2), colspan=2)
  ax4.axis('off')

  # Insolation
  t, _, _, _, signal = run_ins(pars[0], pars[1], pars[2])

  # Simulation
  fit = simulation(ax1, t, signal, sam)

  # Sampling
  sams_con, fits_con = simulations(ax2, t, signal)

  # Variable
  sams_var, fits_var = parameters(ax3, param_ranges)

  # Logistic
  params, covariance = logistic(ax2, sams_con, fits_con)
  params, covariance = logistic(ax3, sams_con, fits_con)

  # Table
  display_tab(ax4, params)

  # Lines
  y = fit
  x_y = find_x_for_y(y, *params)
  x_x = np.interp(y, fits_con, sams_con)
  ax2.axhline(y=y, color='yellow', linestyle='--', linewidth='1', label=f'Average: {x_y:.2f}')
  ax2.axvline(x=x_x, color='magenta', linestyle='--')

  plt.subplots_adjust(hspace=0.8)

  return fig

# ToDo : fix
def update_plot(sam, param_ranges):
  plot_sims(sam, param_ranges)
  clear_output(wait=True)
  time.sleep(0.1)

def plots_sims(sam_values, param_ranges=_A_):
  for sam in sam_values[::-1]:
    update_plot(int(round(sam)), param_ranges)


# Plot Parameters

def func_par(axes, variables):
  for ax, (title, ranges) in zip(axes, variables):
    sams, fits = all(ax, ranges, title)
    params, _ = logistic(ax, sams, fits)
    set_plot_prop(ax, 'log', 'linear', 'samples', 'fit', title, (1, 1e3), (0, 1))

def plot_pars():
  fig, axes = plt.subplots(2, 3, figsize=(20, 8))
  axes = axes.flatten()

  variables = [
    ('Period', _T_),
    ('Amplitude', _A_),
    ('Default', SAM_L),
    ('Period mod', _Tm_),
    ('Amplitude mod', _Am_),
    ('Phase', _p_),
  ]

  func_par(axes, variables)

  plt.subplots_adjust(hspace=0.4)

  return fig


# Web-specific functions
def reset_params():
  """Reset parameters to defaults"""
  global _T1, _T2, _T3, _A1, _A2, _A3, _Tm1, _Tm2, _Tm3, _Am1, _Am2, _Am3
  _T1, _T2, _T3 = int(1.0e5), int(4.1e4), int(2.6e4)
  _A1, _A2, _A3 = int(2), int(25), int(15)
  _Tm1, _Tm2, _Tm3 = int(_T1 * 5), int(_T2 * 5), int(_T3 * 5)
  _Am1, _Am2, _Am3 = int(_A1 / 2), int(_A2 / 2), int(_A3 / 2)
  return "Parameters reset to defaults"

def update_params(**kwargs):
  """Update specific parameters - handle any parameter passed"""
  global _T1, _T2, _T3, _A1, _A2, _A3, _Tm1, _Tm2, _Tm3, _Am1, _Am2, _Am3
  
  # Convert to integers and update
  for key, value in kwargs.items():
    if value is not None:
      int_value = int(value)
      if key == 'T1': _T1 = int_value
      elif key == 'T2': _T2 = int_value
      elif key == 'T3': _T3 = int_value
      elif key == 'A1': _A1 = int_value
      elif key == 'A2': _A2 = int_value
      elif key == 'A3': _A3 = int_value
      elif key == 'Tm1': _Tm1 = int_value
      elif key == 'Tm2': _Tm2 = int_value
      elif key == 'Tm3': _Tm3 = int_value
      elif key == 'Am1': _Am1 = int_value
      elif key == 'Am2': _Am2 = int_value
      elif key == 'Am3': _Am3 = int_value
  
  return f"Parameters updated"

def get_current_params():
  """Get current parameter values as simple dict"""
  return {
    'T1': _T1, 'T2': _T2, 'T3': _T3,
    'A1': _A1, 'A2': _A2, 'A3': _A3,
    'Tm1': _Tm1, 'Tm2': _Tm2, 'Tm3': _Tm3,
    'Am1': _Am1, 'Am2': _Am2, 'Am3': _Am3
  }
