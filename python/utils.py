#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import math

def plotBinaryMap(axes, name, data):
  
  axes.set_title(name)
  axes.set_xlabel('Rows')
  axes.set_ylabel('Columns')
  
  plotW = math.ceil(math.sqrt(len(data)))

  rf = np.zeros([ plotW, plotW ], dtype=np.uint8)
  for i in range(plotW):
    arr = data[i*plotW:i*plotW+plotW]*2
    if len(arr)<plotW:
      arr=np.concatenate([arr, np.ones(plotW-len(arr))])
    rf[:, i] = arr
    
  axes.imshow(rf, interpolation='nearest')
  
def isNotebook():
  try:
      shell = get_ipython().__class__.__name__
      if shell == 'ZMQInteractiveShell':
          return True   # Jupyter notebook or qtconsole
      elif shell == 'TerminalInteractiveShell':
          return False  # Terminal running IPython
      else:
          return False  # Other type (?)
  except NameError:
      return False      # Probably standard Python interpreter
  