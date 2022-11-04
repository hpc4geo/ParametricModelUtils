

from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status
import forward_sh as fm

import numpy as np


def test1():
  M = fm.shModel()
  vals = np.array([2.0])
  M.initialize()
  M.evaluate(vals)
  M.finalize()

  M.name = "forward_sh"
  M.dump()


if __name__ == "__main__":
  test1()
