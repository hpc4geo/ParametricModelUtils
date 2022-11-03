
# python load_model.py --model_module_class_name forward_py:PyModel -d pinput_def_ex1.csv  -n 1 2 3 4 5 6 --model_name xxx

import sys, importlib
import getopt as go
import argparse
import parametric_model as pm


if __name__ == "__main__":
  cmdline_args = pm.CMDA()
  
  parser = argparse.ArgumentParser()
  parser.add_argument('--model_module_class_name', type=str, required=False)
  parser.add_argument('--model_pkl_file', type=str, required=False)
  parser.add_argument('--model_name', type=str, required=False)
  args = parser.parse_known_args(namespace=cmdline_args)

  if cmdline_args.model_module_class_name is not None:
    full_module_name = cmdline_args.model_module_class_name.split(":")[0]
    class_name       = cmdline_args.model_module_class_name.split(":")[1]
    model_module = importlib.import_module(full_module_name)
    print('module:', full_module_name)
    print('class: ', class_name)
    print('mod:   ', model_module)
  
    cls = model_module.__dict__[class_name]
    model = cls.new(parser)
    if cmdline_args.model_name is not None:
      model.name = cmdline_args.model_name
    print('model name:', model.name)
    model.dump()

  if cmdline_args.model_pkl_file is not None:
    if cmdline_args.model_module_class_name is None:
      model = pm.ParametricModel.load(cmdline_args.model_pkl_file)
      print(model)



  """
  args = sys.argv[1:] # skip py script name (first arg)
  
  opts = "n:f:"
  opts_long_name = ["model_name=", "model_pkl_file="]
  arguments, values = go.gnu_getopt(args, opts, opts_long_name)
  
  print(arguments)
  # checking each argument
  for current_arg, current_val in arguments:
    
    if current_arg in ("-n", "--model_name"):
      print("-n val", current_val)

      try:
        print(globals())
        full_module_name = current_val.split(":")[0]
        class_name = current_val.split(":")[1]
        model_module = importlib.import_module(full_module_name)
        print(full_module_name)
        print(class_name)
        print(model_module)
        print(globals())

        #model = model_module.__dict__[class_name]() # call the class constructor - not helpful if we don't know the args

        #model = model_module.__dict__[class_name].new(sys.argv) # call the class constructor
        cls = model_module.__dict__[class_name]
        #print(cls)
        cls.new(sys.argv)


      except:
        raise ImportError('Failed to import the model defined by ' + full_module_name)
          

    if current_arg in ("-f", "--model_pkl_file"):
      print("-f val", current_val)

      model = pm.ParametricModel.load(current_val)

  """
