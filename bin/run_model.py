
import argparse
import parametric_model as pm
import parametric_scheduler as ps
from parametric_model import ExecutionStatus as status


if __name__ == "__main__":
  args = pm.CMDA()

  parser = argparse.ArgumentParser()
  parser.add_argument('--model_pkl_file', type=str, required=True)
  parser.add_argument('--param_file', type=str, required=True)
  parser.parse_known_args(namespace=args)

  M = pm.ParametricModel.load(args.model_pkl_file)

  sch = ps.ParametricScheduler('./output-from-file')
  sch.set_model(M)


  sch.output_path_prefix = 't00'
  jrun, jignore = sch.schedule_from_csv(args.param_file)
  print('ignored', jignore)

  ps.ParametricScheduler.generate_log('./output-from-file', logfname='demo_log.csv')

  sch.cache_generate_log(logfname='demo_cache_log.csv')


  sch.output_path_prefix = 't01'
  jrun, jignore = sch.schedule_from_csv('traj_input_2.csv')
  print('ignored', jignore)
  sch.cache_generate_log(logfname='demo_cache_log_2.csv')
  sch.cache_generate_log(logfname='demo_log_2_err.csv', jstatus=status.ERROR)
  sch.cache_generate_log(logfname='demo_log_2_pend.csv', jstatus=status.UNDEFINED)

  ps.ParametricScheduler.generate_log('./output-from-file', logfname='demo_log_2.csv')

