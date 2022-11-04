

from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status
import forward_slurm as fm

import numpy as np


def test1():
  ts = fm.SlurmModel('pinput_def_ts.csv', 32, 'fullpath/a.out')
  vals = [0.1, 0.2, 11.0]
  ts.initialize()
  ts.evaluate(vals)
  print(ts.exec_status())
  print(ts.stdout)
  ts.finalize()

  ts.name = "forward_slurm"
  ts.dump()


if __name__ == "__main__":
  test1()
