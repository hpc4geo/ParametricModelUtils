

from parametric_model_utils import ParametricInput
from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status
import forward_pyscript as fm

import numpy as np


def test1(): # Check we can instantiate
  
  M = fm.PyscriptModel()

  p_vals = [1.0e3, -2.0, -3.0]
  M.initialize()
  M.evaluate(p_vals)
  M.finalize()
  M.P.write_definition()
  
  M.name = "forward_pyscript"
  M.dump()
  m = pm.ParametricModel.load("forward_pyscript.pkl")


if __name__ == "__main__":
  test1()
