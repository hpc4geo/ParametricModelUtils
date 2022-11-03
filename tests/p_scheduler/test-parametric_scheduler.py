

from parametric_model_utils import parametric_scheduler as ps
from parametric_model_utils import ExecutionStatus as status

import forward_py as fm

import os
import numpy as np


def test_generate():
  ps.ParametricScheduler.generate_log('./output/halton')


def test_push():
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/test_push')
  sch.set_model(M)
  
  p_vals = np.array([[1.0e3, 2.0, 3.4, 14.0],
                     [1.0e4, 2.1, 3.5, 16.0],
                     [1.0e5, 2.2, 3.6, 18.0]])
                     
  jobs_run = sch.run_jobs(p_vals)
  print('jobs run', jobs_run)

  sch2 = ps.ParametricScheduler('./output/test_push')
  sch2.set_model(None)

  jobs_run = sch.run_jobs(p_vals)
  print('jobs run', jobs_run)


def test_smart_push():
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/ps_ex2')
  sch.set_model(M)
  
  p_vals = np.array([[1.0e3, 2.0, 3.4, 14.0],
                     [1.0e4, 2.1, 3.5, 16.0],
                     [1.0e5, 2.2, 3.6, 18.0]])
    
  jobs_run = sch.run_jobs(p_vals)
  print('jobs run', jobs_run)

  flags, run, ignore = sch.filter_run_ignore_from_cache(p_vals)
  print('run 2', run)
  print('ignore 2', ignore)
  
  jobs_run = sch.run_jobs(p_vals[flags])
  print('jobs run 2', jobs_run)


def test_schedule_1():
  """
  Schedule jobs P1 in directory -> jobs run
  Schedule identical  jobs P1 in same directory - all jobs are ignored
  """
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/test_schedule_1')
  sch.set_model(M)
  
  p_vals = np.array([[1.0e3, 2.0, 3.4, 14.0],
                     [1.0e4, 2.1, 3.5, 16.0],
                     [1.0e5, 2.2, 3.6, 18.0]])
    
  jrun, jignore = sch.schedule(p_vals)
  print('jobs run    1', jrun)
  print('jobs ignore 1', jignore)

  jrun, jignore = sch.schedule(p_vals)
  print('jobs run    2', jrun)
  print('jobs ignore 2', jignore)


def test_schedule_2():
  """
  Schedule jobs P1 in directory -> jobs run
  Schedule identical  jobs P1 in same directory - all jobs are ignored
  """
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/test_schedule_2')
  sch.output_path_prefix = 'set1'
  sch.set_model(M)
  
  p_vals = np.array([[1.0e3, 2.0, 3.4, 14.0],
                     [1.0e4, 2.1, 3.5, 16.0],
                     [1.0e5, 2.2, 3.6, 18.0]])
    
  jrun, jignore = sch.schedule(p_vals)
  print('jobs run    1', jrun)
  print('jobs ignore 1', jignore)

  p_vals = np.array([[1.0e3, 2.0, 3.4, 14.0],
                   [1.0e4, 2.1, 3.5, 16.0],
                   [1.2e5, 3.2, 4.6, 28.0],
                   [1.0e4, 2.1, 3.5, 16.0]])

  sch.output_path_prefix = 'set2'
  jrun, jignore = sch.schedule(p_vals)
  print('jobs run    2', jrun)
  print('jobs ignore 2', jignore)



def test_collect_group():
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/group')
  sch.set_model(M)
  
  p_vals = np.array([[1.0e3, 2.0, 3.4, 14.0],
                     [1.0e4, 2.1, 3.5, 16.0],
                     [1.0e5, 2.2, 3.6, 18.0]])
  sch.run_jobs(p_vals)



  traj = ps.ParametricScheduler.collect_valid_trajectories('./output/group')
  print('traj')
  print(traj)

  cache = ps.ParametricScheduler.group_trajectories(traj, M)
  print('cache')
  print('  success  ', cache[status.SUCCESS])
  print('  error    ', cache[status.ERROR])
  print('  undefined', cache[status.UNDEFINED])


def test_schedule_prefix():
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/prefix')
  sch.set_model(M)
  
  sch.output_path_prefix = 'init'
  p_vals1 = np.array([[1.0e3, 2.0, 3.4, 14.0],
                     [1.0e4, 2.1, 3.5, 16.0],
                     [1.0e5, 2.2, 3.6, 18.0]])
    
  jrun, jignore = sch.schedule(p_vals1)
  print('jobs run    1', jrun)
  print('jobs ignore 1', jignore)
  
  sch.output_path_prefix = 'corners'
  p_vals2 = np.array([[2.0e3, 2.0, 3.4, 14.0],
                      [2.0e4, 2.1, 3.5, 16.0],
                      [2.0e5, 2.2, 3.6, 18.0]])
  
  jrun, jignore = sch.schedule(p_vals2)
  print('jobs run    2', jrun)
  print('jobs ignore 2', jignore)


  sch.output_path_prefix = 'ccc'
  jrun, jignore = sch.schedule(p_vals2)
  print('jobs run    3', jrun)
  print('jobs ignore 3', jignore)

  ps.ParametricScheduler.generate_log('./output/prefix')
  sch.cache_generate_log(logfname='demo_log_2.csv')


def test_schedule_prefix_reload():
  test_schedule_prefix()
  print('======')
  coeffs = [2.3, 3.4, 5.66, 7.77]
  sch = ps.ParametricScheduler('./output/prefix')
  sch.set_model(None)
  sch.cache_generate_log(logfname='demo_log_3.csv')


import time


def test_scheduler_n(n):
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/halton/p6')
  sch.set_model(M)
  
  
  #np.random.seed(0)
  """
    delta = 0.0
    for i in range(n):
    p_vals = np.random.random((1,4))
    if i % 1000 == 0:
    print('job index',i, p_vals)
    t0 = time.perf_counter()
    jobs.push(p_vals)
    t1 = time.perf_counter()
    delta += t1 - t0
    print('time', delta)
    """
  
  
  #np.random.seed(0)
  p_vals = np.random.random((n,4))
  delta = 0.0
  t0 = time.perf_counter()
  sch.schedule(p_vals)
  t1 = time.perf_counter()
  delta += t1 - t0
  print('time', delta)


def test3():
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = PyModel('pinput_def_ex1.csv', coeffs)
  
  jobs = ps.ParametricScheduler('./output/halton')
  jobs.set_model(M)
  
  d = jobs.push_from_csv('traj_input.csv')
  jobs.push(d)


def test_batch():
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel('pinput_def_ex1.csv', coeffs)
  
  sch = ps.ParametricScheduler('./output/batch')
  sch.set_model(M)

  p_vals = np.array([[1.0e3, 2.0, 3.4, 14.0],
                    [1.0e4, 2.1, 3.5, 16.0],
                    [1.0e5, 2.2, 3.6, 18.0]])
  
  jrun, jignore = sch.schedule(p_vals)

  udef = dict(sch.cache[status.SUCCESS])
  print(len(udef))

  print(sch.wait_all(1.0))


if __name__ == "__main__":
  #test_push()
  #test_smart_push()
  #test_collect_group()
  
  #test_schedule_1()
  #test_schedule_2()
  #test_schedule_prefix_reload()

  #test_schedule_prefix()

  test_batch()
