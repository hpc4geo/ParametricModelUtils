

from parametric_model_utils import ParametricInput
from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status

import os
import numpy as np
import subprocess


class PyscriptModel(pm.ParametricModel):
  
  def __init__(self, **kwargs):
    
    P = ParametricInput(None, _params=[
                                       {"name": 'a', "bounds":[0.0, 10.0], "units":'-'},
                                       {"name": 'b', "bounds":[0.0, 2.0], "units":'-'},
                                       {"name": 'c', "bounds":[-10.0, 1.0], "units":'-'},
                                       ] )
    P.write_definition()
    os.rename("parametric_def.csv", "pyscript_parametric_def.csv")
    super().__init__("pyscript_parametric_def.csv", **kwargs)
  

  def evaluate(self, params):
    p = self.P._convert(params)
    proc = subprocess.Popen( ["python", "sum_numbers.py", str(p['a']), str(p['b']), str(p['c'])],
                            stdin=None, stdout=None, stderr=None)

  def exec_status(self):
    return status.SUCCESS

