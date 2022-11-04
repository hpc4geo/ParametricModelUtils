

from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status
import forward_py as fm

import numpy as np


def test1(): # Check we can instantiate
  coeffs = [2.3, 3.4, 5.66, 7.77]
  M = fm.PyModel("pinput_def_ex1.csv", coeffs)

  p_vals = [1.0e3, -2.0, -3.0, -4.0]
  M.initialize()
  M.evaluate(p_vals)
  M.finalize()
  M.P.write_definition()
  
  M.name = "forward_py"
  M.dump()
  m = pm.ParametricModel.load("forward_py.pkl")

  print('job status   :', M.exec_status())
  print('observable      :', M.get_observable(), type(M.get_observable()))


if __name__ == "__main__":
  test1()
  print(fm.PyModel)
