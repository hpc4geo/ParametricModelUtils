


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

  def __init__(self, input_def, nx, executable, **kwargs):
    try:
      super().__init__(input_def, kwargs['name'])
    except:
      super().__init__(input_def)
    
    self.nx = nx
    self.executable = executable
    self.stdout = None

  def initialize(self):
    pass

  def finalize(self):
    self.stdout = None
    pass


  def evaluate(self, params):
    p = self.P._convert(params)
    
    sfilename = os.path.join(self.output_path, 'job.slurm')
    with open(sfilename, "w") as fp:
      fp.write('#!/bin/bash' + '\n')
      fp.write('# auto-generated slurm file' + '\n')
      fp.write('# mpiexec -n 3 ' + self.executable + '\n')
      fp.write('ls ' + self.output_path + '\n')
      fp.write('touch job.sentinel' + '\n')

    #slurm_stdout = subprocess.run(["sbatch", "job.slurm"], capture_output=True, text=True)
    slurm_stdout = subprocess.run(["sh", "job.slurm"], capture_output=True, text=True)
    self.stdout = slurm_stdout.stdout

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
