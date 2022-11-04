
# Usage
# [1] Generate a pickle file
# cd examples/forward_model
# python test_forward_model_py.py
# [2] Run some parameters
# python bin/run_model.py --model_pkl_file examples/forward_models/forward_py.pkl --param_file examples/forward_models/traj_input_forward_py.csv --model_module_class_name examples/forward_models:forward_py

import sys, argparse
import importlib

from parametric_model_utils import parametric_model as pm
from parametric_model_utils import parametric_scheduler as ps
from parametric_model_utils import ExecutionStatus as status


if __name__ == "__main__":
  args = pm.CMDA()

  parser = argparse.ArgumentParser()
  parser.add_argument('--model_module_class_name', type=str, required=True) # path:module [don't include .py]
  parser.add_argument('--model_pkl_file', type=str, required=True)
  parser.add_argument('--param_file', type=str, required=True)
  parser.parse_known_args(namespace=args)

  module_path = args.model_module_class_name.split(":")[0]
  module_name       = args.model_module_class_name.split(":")[1]

  if module_path != "":
    sys.path.append(module_path)
  model_module = importlib.import_module(module_name)

  M = pm.ParametricModel.load(args.model_pkl_file)

  sch = ps.ParametricScheduler('./output/from-file')
  sch.set_model(M)

  sch.output_path_prefix = 't00'
  jrun, jignore = sch.schedule_from_csv(args.param_file)
  print('ignored', jignore)

  sch.cache_generate_log(logfname='demo_cache_log.csv')

