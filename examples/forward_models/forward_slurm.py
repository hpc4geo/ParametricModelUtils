


from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status

import os
import numpy as np
import subprocess

# job_completed = false implies observable_valid = false

# [1] Create slurm file. No slurm file imples job_completed = false, job_pending  = false, job_successful = false, observable_valid = false
# [2] Call sbatch. Within slurm file, after each executable call `touch job.sentinel`.
#     If slurm file exists but job.job.sentinel is not found found, job_pending = true and job_compl

def python_task():
  pass

class SlurmModel(pm.ParametricModel):
  
  def __init__(self, input_def, nx, model_path, **kwargs):
    try:
      super().__init__(input_def, kwargs['name'])
    except:
      super().__init__(input_def)
    
    self.nx = nx
    self.model_path = model_path
    
    os.makedirs(model_path, exist_ok=True)
  

  def initialize(self):
    os.makedirs(os.path.join(self.output_path, 'output'), exist_ok=True)


  def finalize(self):
      return


  def evaluate(self, params):
    p = self.P._convert(params)
    
    sfilename = os.path.join(self.output_path, 'job.slurm')
    with open(sfilename, "w") as fp:
      fp.write('# auto-generated slurm file')

    cmd = 'sbatch ' + sfilename

    #slurm_stdout = subprocess.run(["ls", self.output_path], capture_output=True)
    #print(slurm_stdout.stdout.decode())
    slurm_stdout = subprocess.run(["ls", self.output_path], capture_output=True, text=True)
    print(slurm_stdout.stdout)


  def exec_status(self):
    fname = os.path.join(self.output_path, 'job.slurm')
    found = os.path.exists(fname)
    if found == False:
      return status.ERROR
    else:
      fname = os.path.join(self.output_path, 'job.sentinel')
      found = os.path.exists(fname)
      if found == True:
        return status.SUCCESS
      else:
        return status.UNDEFINED


def test1():
  ts = SlurmModel('pinput_def_ts.csv', 32, 'ts_mesh')
  vals = [0.1, 0.2, 11.0]
  ts.initialize()
  ts.evaluate(vals)
  ts.finalize()




if __name__ == "__main__":
  test1()
