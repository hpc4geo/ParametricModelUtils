

from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status

import os
import numpy as np
import subprocess
import time

# This model
#   [1] creates a bash script called demo_job.sh
#   [2] calls the bash script
# At the end of the script, an empty file job.sentinel is generated.
# The model exec_status is considered successful if job.sentinel exists.
# The model exec_status is considered undefined if demo_job.sh exists but job.sentinel does not.
# The model exec_status is considered to be an error if neither file (.sh or .sentinel) exists

class shModel(pm.ParametricModel):


  def __init__(self, **kwargs):
    super().__init__('pinput_def_sh.csv', **kwargs)


  def evaluate(self, params):
    self.P.write(params)
    p = self.P._convert(params)
    print(p)
    fp = open(os.path.join(self.output_path, 'demo_job.sh'), "w")
    fp.write('#!/bin/bash' + '\n')
    fp.write('sleep ' + str(p["T"])  + '\n')
    fname = os.path.join(self.output_path, 'job.sentinel')
    fp.write('touch ' + fname + '\n')
    fp.close()

    # This does not detach the process
    #print('waiting for', p["T"], 'sec')
    #process = subprocess.run(["sh", os.path.join(self.output_path, 'demo_job.sh'), "&"], capture_output=True, text=True, shell=True)
    #process = subprocess.run(["sh", os.path.join(self.output_path, 'demo_job.sh'), "&"], text=True)
    #print(process)
    #print('[stdout]', process.stdout)

    proc = subprocess.Popen( ["sh", os.path.join(self.output_path, 'demo_job.sh')],
                 stdin=None, stdout=None, stderr=None)
    print(proc, 'wait time', p["T"])
    time.sleep(0.5)

  def exec_status(self):
    fname = os.path.join(self.output_path, 'job.sentinel')
    found = os.path.exists(fname)
    if found: return status.SUCCESS
    
    fname = os.path.join(self.output_path, 'demo_job.sh')
    found = os.path.exists(fname)
    if found: return status.UNDEFINED
    else: return status.ERROR


def test1():
  M = shModel()
  vals = np.array([2.0])
  M.initialize()
  M.evaluate(vals)
  M.finalize()


if __name__ == "__main__":
  test1()
  #test_schedule()
