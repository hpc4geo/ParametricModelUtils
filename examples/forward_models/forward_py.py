

from parametric_model_utils import parametric_model as pm
from parametric_model_utils import ExecutionStatus as status

import os
import numpy as np


class PyModel(pm.ParametricModel):
  
  def __init__(self, input_def, numbers, **kwargs):
    super().__init__(input_def, **kwargs)
    #pm.ParametricModel.__init__(self, input_def, **kwargs)
    #super(PyModel, self).__init__(input_def, **kwargs)
    
    self.coeff = list(numbers)
    self.exit_code_fname = 'pymodel.ierr'
    self.obs_fname = 'obs_pymodel.txt'


  def write_observable(self, value):
    base_dir = self.output_path
    fp = open( os.path.join(base_dir, self.obs_fname), 'w')
    fp.write(str(value))
    fp.close()


  def write_exit_code(self, value):
    base_dir = self.output_path
    fp = open( os.path.join(base_dir, self.exit_code_fname), 'w')
    if value < 0:
      fp.write(str(1))
    else:
      fp.write(str(0))
    fp.close()


  def get_exit_code(self):
    base_dir = self.output_path
    fp = open( os.path.join(base_dir, self.exit_code_fname), 'r')
    v = fp.read()
    fp.close()
    return int(v)


  def evaluate(self, params):
    base_dir = self.output_path

    p = self.P._convert(params)
    vals = list(p.values())
    
    v = 0.0
    for i in range(len(self.coeff)):
      v += self.coeff[i] * vals[i]
    
    # log the success of the job
    self.write_exit_code(v)

    # log the observable
    self.write_observable(v)


  # If pymodel.ierr exists - job has run => True
  def exec_status(self):
    base_dir = self.output_path
    found = os.path.exists( os.path.join(base_dir, self.exit_code_fname))
    if found:
      ierr = self.get_exit_code()
      if ierr == 0: return status.SUCCESS
      else:         return status.ERROR
    else:
      return status.UNDEFINED


  # Load obs_pymodel.txt
  def get_observable(self):
    base_dir = self.output_path
    found = os.path.exists( os.path.join(base_dir, self.obs_fname))
    if found:
      fp = open( os.path.join(base_dir, self.obs_fname), 'r')
      v = fp.read()
      fp.close()
      return np.array(float(v))
    else:
      raise RuntimeError('Observable invalid - cannot load it')


  @classmethod
  def new(cls, parser):
    cmdline_args = pm.CMDA()
  
    parser.add_argument('-d', '--param_def', type=str, required=True)
    # usage --param_def=pinput_def_ex1.csv  or  -d=pinput_def_ex1.csv
    #       --param_def pinput_def_ex1.csv  or  -d pinput_def_ex1.csv
    
    parser.add_argument('-n', '--numbers', nargs='+', type=float, required=True)
    # usage --numbers 0 1 2
    
    args = parser.parse_known_args(namespace=cmdline_args)

    print('  PyModel <input>:', cmdline_args.param_def)
    print('  PyModel <input>:', cmdline_args.numbers)

    model = PyModel(cmdline_args.param_def, cmdline_args.numbers)
    model.name = "default_PyModel"
    return model
