
import os
import pickle
from abc import ABC, abstractmethod
from .parametric_input import ParametricInput


class CMDA: # cmdline_args
  pass


from enum import Enum
class ExecutionStatus(Enum):
  SUCCESS   = 1
  ERROR     = 2
  UNDEFINED = 3

class ParametricModel(ABC):

  def __init__(self, input_def, **kwargs):
    self.P = ParametricInput(input_def)
    self._name = 'default_pmodel'
    k = list(kwargs.keys())
    if "name" in k:
      self._name = kwargs["name"]

    self._output_path = ''


  @property
  def name(self):
    return self._name
  @name.setter
  def name(self, uname):
    self._name = uname


  @property
  def output_path(self):
    return self._output_path
  @output_path.setter
  def output_path(self, dname):
    self._output_path = dname


  def initialize(self):
    pass

  @abstractmethod
  def evaluate(self, param):
    pass


  def finalize(self):
    pass


  @abstractmethod
  def exec_status(self):
    """Returns ExecutionStatus.{SUCCESS, ERROR, UNDEFINED}"""
    pass


  @classmethod
  def new(cls, parser):
    """
    Processes command line args and call a derived ParametericModel constructor.
    `parser` is variable obatined from calling `argparse.ArgumentParser()`.
    """
    raise RunTimeError('The ABC `ParametricModel` does not define `new()`')


  def get_observable(self):
    """Return params and a numpy.ndarray or meta-data associated with an observable (e.g. a file name)."""
    raise NotImplementedError('Must over-ride definition of `get_observable()`')


  @classmethod
  def load(cls, fname):
    model = pickle.load(open(fname, "rb"))
    return model


  def dump(self, output_path=""):
    fname = os.path.join(output_path, self.name + ".pkl")
    pickle.dump(self, open(fname, "wb"))


  def __str__(self):
    view = self.__class__.__name__ + ':\n'
    view += '  name = ' + self.name + '\n'
    view += '  output_dir = ' + str(self.output_path) + '\n'
    view += '  ' + str(self.P) + '\n'
    view += '  ' + str(self.initialize) + '\n'
    view += '  ' + str(self.evaluate) + '\n'
    view += '  ' + str(self.finalize) + '\n'
    view += '  ' + str(self.exec_status) + '\n'
    view += '  ' + str(self.get_observable)
    return view


# Summary of tests
# 1 -> try to instantiate abstract class
# 2 -> check inheritence
# 3 ->

def test1(): # Test instantiating abstract base class fails
  M = ParametricModel("pinput_def_ex1.csv")


class PModel(ParametricModel):
  def evaluate(self): pass
  def exec_status(self): return ExecutionStatus.SUCCESS
  def initialize(self):
    print('PModel init')
    self.output_path = "xyz"


def test2(): # Test instantiating inherited class with appropriate methods is sucessful
  M = PModel("pinput_def_ex1.csv")
  print(M)
  
  M.initialize()
  #M.output_path = "xxx"
  print(M.output_path)

if __name__ == "__main__":
  #test1()
  test2()

  print(ExecutionStatus.ERROR)
