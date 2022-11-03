

from parametric_model_utils import parametric_model as pm

import forward_py as fm

import os
import numpy as np


def test1():
  """
  Test ParametricModel functionality
  - initialize(), evaluate(), finalize()
  """
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel("pinput_def_ex1.csv", coeffs)

  p_vals = [1.0e3, -2.0, -3.0, -4.0]
  M.output_path = './'
  M.initialize()
  M.evaluate(p_vals)
  M.finalize()

  print('job status:', M.exec_status())
  print('observable:', M.get_observable(), type(M.get_observable()))


def test4():
  """
  Test ParametricModel functionality
  - dump() and load()
  """
  
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs, name='poly')
  
  p_vals = [1.0e3, -2.0, -3.0, -4.0]
  M.output_path = './'
  M.initialize()
  M.evaluate(p_vals)
  M.finalize()
  
  print('model name      :', M.name)
  print('job status:', M.exec_status())
  print('observable:', M.get_observable(), type(M.get_observable()))

  M.dump()
  print(M)

  M1 = pm.ParametricModel.load('poly.pkl')
  print(M1)
  p_vals = [1.0e3, -2.0, -3.0, -4.0]
  M.output_path = './'
  M.initialize()
  M.evaluate(p_vals)
  M.finalize()


if __name__ == "__main__":
  test1()
  #test4()
