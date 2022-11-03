

from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status

import os
import numpy as np


class TSModel(pm.ParametricModel):
  
  def __init__(self, input_def, nx, model_path, **kwargs):
    super().__init__(input_def, **kwargs)
    
    self.t1 = 2.2
    self.nt = 19
    self.dt = self.t1 / float(self.nt)

    self.nx = nx
    self.x = np.linspace(0.0, 1.0, nx)

    self.model_path = model_path
    os.makedirs(model_path, exist_ok=True)
    np.savetxt(os.path.join(model_path,'x_coor.txt'), self.x)
    

  def initialize(self):
    base_dir = self.output_path
    os.makedirs(os.path.join(base_dir, 'output'), exist_ok=True)


  def finalize(self):
      return


  def evaluate(self, params):
    base_dir = self.output_path
    
    p = self.P._convert(params)
    
    time = np.linspace(0.0, self.t1, self.nt)
    idx = 0
    for t in time:
      f = p["a"] + np.sin( 2.0 * np.pi * (p["b"] * self.x + p["w"] * t) )
      np.savetxt(os.path.join(base_dir,'output', 't'+str(idx)+'.txt'), f)
      idx += 1
    
    with open(os.path.join(base_dir, 'output', 'ts.log'), "w") as fp:
      fp.write(str(idx))


  # If job_completed() == True and pymodel.ierr cpntains 0 => True
  def exec_status(self):
    base_dir = self.output_path
    fname = os.path.join(base_dir, 'output', 'ts.log')
    found = os.path.exists(fname)
    if found:
      with open(os.path.join(base_dir, 'output', 'ts.log'), "r") as fp:
        steps = int(fp.read())
        if steps == self.nt:
          return status.SUCCESS
        else:
          return status.ERROR
    else:
      return status.UNDEFINED

  # Load obs_pymodel.txt
  def get_observable(self):
    base_dir = self.output_path
    fname = os.path.join(base_dir, 'output', 'ts.log')
    found = os.path.exists(fname)
    if found:
      return os.path.join(base_dir, 'output')
    else:
      raise RuntimeError('Observable invalid - cannot load it')


def test1():
  ts = TSModel('pinput_def_ts.csv', 32, 'ts_mesh')
  vals = [0.1, 0.2, 11.0]
  ts.initialize()
  ts.evaluate(vals)
  ts.finalize()
  print(ts.exec_status())


"""
import parametric_scheduler as ps

def test2():
  root_path = './suite1'
  ts = TSModel('pinput_def_ts.csv', 32, os.path.join(root_path, 'ts_mesh'))
  vals = np.array([[0.1, 0.2, 11.0]])
  jobs = ps.ParametricScheduler(root_path)
  jobs.set_model(ts)
  jobs.push(vals)
"""

if __name__ == "__main__":
  test1()
