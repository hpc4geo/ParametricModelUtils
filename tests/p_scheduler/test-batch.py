

from parametric_model_utils import parametric_scheduler as ps
from parametric_model_utils import ExecutionStatus as status

from forward_py import PyModel
from forward_sh import shModel

import os
import numpy as np



def test_wait_all():
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/batch')
  sch.set_model(M)

  p_vals = np.array([[1.0e3, 2.0, 3.4, 14.0],
                    [1.0e4, 2.1, 3.5, 16.0],
                    [1.0e5, 2.2, 3.6, 18.0]])
  
  jrun, jignore = sch.schedule(p_vals)

  udef = dict(sch.cache[status.SUCCESS])
  print(len(udef))

  print(sch.wait_all(1.0))



# Run this example multiple times in quick succession
def test_probe():
  
  M = shModel()
  sch = ps.ParametricScheduler('./output-async')
  sch.set_model(M)
  
  """
    nnew = sch.flush()
    print('cache-x', sch.cache)
    print('nnew ', nnew)
    """
  
  p_vals = np.array([[4.0],
                     [0.001],
                     [1.0]])
    
  jrun, jignore = sch.schedule(p_vals)
  print('jobs run   ', jrun)
  print('jobs ignore', jignore)

  print('cache-i ', sch.cache)

  nnew = sch.probe(5.0)
  print('cache-ii', sch.cache)
  print('nnew ', nnew)


def test_batch():
  np.random.seed(0) # For deterministic runs

  M = shModel()
  sch = ps.ParametricScheduler('./output-batch')
  sch.set_model(M)

  ntraj = 4
  pv = np.random.random(ntraj)
  pv *= 7.7 # scale numbers s.t. (0,7.7)
  p_vals = np.array(pv).reshape((ntraj,1))

  jrun, jignore = sch.schedule(p_vals)
  nscans = sch.wait_all(1.0)
  print(nscans)


def test_batch2():
  np.random.seed(0) # For deterministic runs
  
  M = shModel()
  sch = ps.ParametricScheduler('./output-batch')
  sch.set_model(M)
  
  ntraj = 12
  pv = np.random.random(ntraj)
  pv *= 2.7 # scale numbers s.t. (0,7.7)
  p_vals = np.array(pv).reshape((ntraj,1))
  

  run, ignore = sch.batched_schedule(p_vals, max_jobs=4, wait_time=5.0)
  nscans = sch.wait_all(1.0)

  print('run', run)
  print('ignore', ignore)



if __name__ == "__main__":
  #test_wait_all()
  #test_probe()
  #test_batch()
  test_batch2()
