

from parametric_model_utils import parametric_scheduler as ps
from parametric_model_utils import ExecutionStatus as status

import forward_py as fm

import os
import numpy as np
import time

np.random.seed(0)

def test_large(Ngroups, Ntraj):
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/large')
  sch.set_model(M)
  
  for i in range(Ngroups):
    sch.output_path_prefix = 'set_' + str(i)
    p_vals = np.random.random( (Ntraj, 4))
    jrun, jignore = sch.schedule(p_vals)



if __name__ == "__main__":

  tA = time.perf_counter()
  #test_large(1, 10000) # 32 sec / 2.2 sec
  test_large(100, 100) # 25 sec / 1.9 sec
  #test_large(1000, 10) # 30 sec / 2.1 sec
  tB = time.perf_counter()
  
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  t0 = time.perf_counter()
  sch = ps.ParametricScheduler('./output/large')
  sch.set_model(None)
  t1 = time.perf_counter()
  print('time[run]    ', tB - tA)
  print('time[rebuild]', t1 - t0)
