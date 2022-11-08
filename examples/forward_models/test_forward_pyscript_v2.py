

from parametric_model_utils import ParametricInput
from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status
import forward_pyscript_v2 as fm

import numpy as np
import time

def test1(): # Check we can instantiate
  
  M = fm.PyscriptModel()

  p_vals = [1.0e3, -2.0, -3.0]
  M.initialize()
  M.evaluate(p_vals)
  M.finalize()
  M.P.write_definition()

  time.sleep(2.0)
  print('exec_status()', M.exec_status())
  print(M.process)
  print(M.process.stdout)
  time.sleep(2.0)
  print('exec_status()', M.exec_status())
  (out, err) = M.process.communicate();
  print("returned code = %d" % M.process.returncode)
  print("output:%s" % out)
  print("errors:%s" % err)
  print('exec_status()', M.exec_status())

  M.name = "forward_pyscript"
  M.initialize() # Must set M.process = None for pickle to work.
  M.dump()
  m = pm.ParametricModel.load("forward_pyscript.pkl")


if __name__ == "__main__":
  test1()
