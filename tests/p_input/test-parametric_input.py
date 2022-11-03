
# Either style works
from parametric_model_utils import parametric_input as pi
#import parametric_model_utils as pi

import numpy as np


def test1():
  """
  Tests ParametricInput functionality
  - viewer
  - .write_definition() -> parametric_def.csv
  - .write() -> params.csv
  - .write_json() -> params.json
  - .create_database_record()
  - ._convert() for dict(), ndarray and list inputs for a single trajectory
  - .get_identifier()
  """
  problem = pi.ParametricInput('pinput_def_ex1.csv')
  print(problem)
  
  problem.write_definition()

  # Flip the ordering of n, T0 to check convert() performs the correct ordering
  p1 = { "velocity": 1.1, "mu": 0.0, "n": 2.0, "T0": 444.0 }
  print('p1', problem._convert(p1))

  p1 = { "velocity": 2, "mu": -3, "n": 3, "T0": 5.000002 }
  print('p1', problem._convert(p1))

  p2 = np.array([2, -3, 5.000002, 3])
  print('p2', problem._convert(p2))

  p3 = [float(2), float(-3), 5.000002, float(3)]
  print('p3', problem._convert(p3))

  d = problem.get_identifier(p1)
  print('id[p1]', d)
  d = problem.get_identifier(p2)
  print('id[p2]', d)
  d = problem.get_identifier(p3)
  print('id[p3]', d)

  p3 = [float(2), float(-3), 5.000002, float(3)]
  d = problem.get_identifier(p3)
  print('id', d)

  problem.write(p1)

  problem.write_json(p1)

  line = problem.create_database_record(p1)
  print(line)


def test2():
  """
  Tests ParametricInput functionality
  - ._convert() for dict(), ndarray and list inputs for multiple trajectories
  - .get_identifiers()
  """
  problem = pi.ParametricInput('pinput_def_ex1.csv')

  p1 = { "velocity": 2.0, "mu": -3.0, "n": 2.0, "T0": 444.0 }
  print('p1 (dict ->)', problem._convert(p1))
  
  p2 = np.array([2, -3, 5.000002, 3])
  print('p2 (np.ndarray[1d] as vec ->)', problem._convert(p2))

  p3 = [2.0, -3.0, 5.000002, 3.0]
  print('p3 (list ->)', problem._convert(p3))

  p4 = np.array([[2.0, -3.0, 5.000002, 3.0], [2.4, -3.4, 15.000002, 3.8]], dtype=np.float64)
  print(p4)
  print('p4 (np.ndarray[2d] ->)', problem._convert(p4))

  p5 = [[2.0, -3.0, 5.000002, 3.0], [2.4, -3.4, 15.000002, 3.8]]
  print(p5)
  print('p5 (list[list] ->)', problem._convert(p5))

  d = problem.get_identifiers(p5)
  print('ids', d)


def test3():
  problem = pi.ParametricInput('pinput_def_ex1.csv')
  print(problem)
  
  p = { "velocity": 2.0, "mu": -3.0, "n": 2.0, "T0": 444.0 }
  print('p (dict ->)', problem._convert(p))
  try:
    print(problem.get_identifier(p))
  except:
    pass

  p = np.array([[2.0, -3.0, 5.000002, 3.0], [2.4, -3.4, 15.000002, 3.8]], dtype=np.float64)
  print('p (np.ndarray[2d] ->)', problem._convert(p))
  try:
    print(problem.get_identifier(p))
  except:
    pass


def test4():
  """
  Tests ParametricInput functionality
  - Check behaviour for 40 dimensional parameter space
  """
  problem = pi.ParametricInput('pinput_def_40p.csv')
  print(problem)
  
  p = np.random.random((300, 40))
  print('p (np.ndarray[2d] ->)', problem._convert(p))
  try:
    print(problem.get_identifier(p))
  except:
    pass

  for i in range(p.shape[0]):
    param_i = np.array(p[i, :])
    phash = problem.get_identifier(param_i)
  print(problem.get_identifier(param_i))
  print(problem.get_identifiers(param_i))


if __name__ == "__main__":
  #test1()
  #test2()
  #test3()
  test4()
