

from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status
import forward_ts as fm

import numpy as np


def test1():
  ts = fm.TSModel('pinput_def_ts.csv', 32, 'ts_mesh')
  vals = [0.1, 0.2, 11.0]
  ts.initialize()
  ts.evaluate(vals)
  ts.finalize()
  print(ts.exec_status())

  ts.name = "forward_ts"
  ts.dump()


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
