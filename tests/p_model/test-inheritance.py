
from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status


# Summary of tests
# 1 -> try to instantiate abstract class
# 2 -> check inheritence

def test1():
  """
  Test instantiating abstract base class fails
  """
  M = pm.ParametricModel("pinput_def_ex1.csv")


class PModel(pm.ParametricModel):
  def evaluate(self): pass
  def exec_status(self): return status.SUCCESS
  def initialize(self):
    print('PModel init():')
    self.output_path = "xyz"


def test2():
  """
  Test instantiating inherited class with appropriate methods is sucessful
  """
  M = PModel("pinput_def_ex1.csv")
  print(M)
  
  M.initialize()
  M.output_path = "xxx"
  print(M.output_path)


if __name__ == "__main__":
  #test1()
  test2()

  print('status[SUCCESS]', status.SUCCESS)
  print('status[ERROR]', status.ERROR)
  print('status[UNDEFINED]', status.UNDEFINED)
