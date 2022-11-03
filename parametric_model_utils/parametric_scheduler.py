
import os
import numpy as np
import time
import pathlib
from .parametric_input import ParametricInput
from .parametric_model import ParametricModel
from .parametric_model import ExecutionStatus as status


class ParametricScheduler:
  """
  The schedular takes a ParametricModel and runs instances of it with different parameter values.
  The scheduler is stateless.
  It does not store anything other than the path where to write all output.
  """

  def __init__(self, root_dir="./"):
    self.root_dir = root_dir

    found = os.path.exists(self.root_dir)
    if found:
      print('[+scheduler] Root path', self.root_dir, 'exists')
    else:
      os.makedirs(self.root_dir, exist_ok=True)
      print('[+scheduler] Root path', self.root_dir, 'created')

    # Initialize attributes
    self._output_path_prefix = ''
    
    self.model = None
    self.P = None
    self.phash = None
    self.cache = { status.SUCCESS: dict(), status.ERROR: dict(), status.UNDEFINED: dict() }

  @property
  def output_path_prefix(self):
    return self._output_path_prefix
  @output_path_prefix.setter
  def output_path_prefix(self, dname):
    self._output_path_prefix = dname
    os.makedirs(os.path.join(self.root_dir, self._output_path_prefix), exist_ok=True)
    print('[+scheduler] New path', os.path.join(self.root_dir, self._output_path_prefix), 'created')


  def get_job_output_path(self, p):
    param_hash = self.P.get_identifier(p)
    relative_jdir = os.path.join(self.root_dir, self.output_path_prefix, param_hash)

    if param_hash in self.cache[status.SUCCESS]:
      relative_jdir = self.cache[status.SUCCESS][param_hash][1]
    if param_hash in self.cache[status.ERROR]:
      relative_jdir = self.cache[status.ERROR][param_hash][1]
    if param_hash in self.cache[status.UNDEFINED]:
      relative_jdir = self.cache[status.UNDEFINED][param_hash][1]

    return relative_jdir, param_hash


  def set_model(self, model):
    
    if self.model is not None:
      raise RuntimeError('ParametricScheduler already has a model defined')

    fname = 'parametric_def.csv'
    fname = os.path.join(self.root_dir, fname)
    found = os.path.exists(fname)

    if not found and model is None:
      raise RuntimeError('ParametricScheduler requires a model be provided')
    
    if found and model is None:
      print('[+scheduler] Scanning', self.root_dir, 'for saved ParametricModel')
    
      onlyfiles = [f for f in os.listdir(self.root_dir) if os.path.isfile(os.path.join(self.root_dir, f))]
      for f in onlyfiles:
        if ".pkl" in f:
          print('  [+scheduler] Attempting to load', f, 'as a ParametricModel')
          try:
            m = ParametricModel.load(os.path.join(self.root_dir, f))
            model = m
          except:
            pass
      
      if model is None:
        raise RuntimeError('A pkl file defining a ParametricModel was not found')
  
    if found == False:
      print('[+scheduler] Writing parameter definition')
      model.P.write_definition(self.root_dir)
      model.dump(self.root_dir)
      new_job_sequence = True
    else:
      new_job_sequence = False
      print('[+scheduler] Existing parameter definition found. Validating')
      data = np.genfromtxt(fname, comments="#", delimiter=" ", dtype=str)
      data = np.atleast_2d(data)
      if data.shape[0] != len(model.P.param_names):
        raise RuntimeError('  Parametric model is inconsistent with existing model definition (num. params differs)')
      for i in range(len(model.P.param_names)):
        key = model.P.param_names[i]
        if model.P.param_names[i] != data[i, 0]:
          raise RuntimeError('  Parametric model is inconsistent with existing model definition (name differs)')
        if str(model.P.param_bounds[key][0]) != data[i, 1]:
          raise RuntimeError('  Parametric model is inconsistent with existing model definition (bound[0] differs)')
        if str(model.P.param_bounds[key][1]) != data[i, 2]:
          raise RuntimeError('  Parametric model is inconsistent with existing model definition (bound[1] differs)')
        if model.P.param_units[key] != data[i, 3]:
          raise RuntimeError('  Parametric model is inconsistent with existing model definition (unit differs)')

    self.M = model
    self.P = model.P
    self.phash = self.P.generate_phash()

    if not new_job_sequence:
      # Collect valid models
      # Re-build cache
      traj = ParametricScheduler.collect_valid_trajectories(self.root_dir)
      self.cache = ParametricScheduler.group_trajectories(traj, self.M)


  def filter_run_ignore_from_cache(self, params):
    """
    Returns
      `to_eval` np.ndarray filled with boolean values indicating whether param[i] should be run.
      `run` dict defined by param_hash: [ [list-of-params], output_path, reason-job-is-to-be-run ]
      `ignore` dict defined by param_hash: [ [list-of-params], output_path, reason-job-is-NOT-to-be-run ]
    """
    run = dict()
    ignore = dict()
    
    nparam_instances = params.shape[0]
    to_eval = np.array([False] * nparam_instances)
    
    for i in range(nparam_instances):
      param_i = params[i, :]
      
      #param_hash = self.P.get_identifier(param_i)
      #relative_jdir = os.path.join(self.root_dir, param_hash)
      relative_jdir, param_hash = self.get_job_output_path(param_i)
      abs_jdir = os.path.abspath(relative_jdir)
      
      run_task = False
      reason = 'reason-initialized'
      
      if param_hash in self.cache[status.SUCCESS]:
        run_task = False
        reason = 'job defines non-unique params, exec_status() = SUCCESS => ignoring'
        # update relative path
        vals = self.cache[status.SUCCESS][param_hash]
        relative_jdir = vals[1]
        abs_jdir = os.path.abspath(relative_jdir)
      
      elif param_hash in self.cache[status.UNDEFINED]:
        run_task = False
        reason = 'job defines non-unique params, exec_status() = UNDEFINED. Likely job pending in queue => ignoring'
        # update relative path
        vals = self.cache[status.UNDEFINED][param_hash]
        relative_jdir = vals[1]
        abs_jdir = os.path.abspath(relative_jdir)
      
      elif param_hash in self.cache[status.ERROR]:
        run_task = True
        reason = 'job defines non-unique params, exec_status() = ERROR => re-run job'
        # update relative path
        vals = self.cache[status.ERROR][param_hash]
        relative_jdir = vals[1]
        abs_jdir = os.path.abspath(relative_jdir)
      
      else:
        # param_hash is not an any list of validate models, so it's considered as a new job
        run_task = True
        reason = 'job defines unique params'

      if run_task:
        run.update( {param_hash: [list(param_i), relative_jdir, reason]} )
        to_eval[i] = True
      else:
        ignore.update( {param_hash: [list(param_i), relative_jdir, reason]} )
        to_eval[i] = False
  
    return to_eval, run, ignore


  def run_jobs(self, params):
    tasks_run = dict()
    
    nparam_instances = params.shape[0]
    for i in range(nparam_instances):
      param_i = params[i, :]
      
      #jdir = self.M.P.get_identifier(param_i)
      #relative_jdir = os.path.join(self.root_dir, jdir)
      relative_jdir, jdir = self.get_job_output_path(param_i)
      abs_jdir = os.path.abspath(relative_jdir)

      found = os.path.exists(abs_jdir)
      if found == False:
        ierr = pathlib.Path(abs_jdir).mkdir(parents=False, exist_ok=False)
          
      self.M.output_path = abs_jdir
      self.M.initialize()
        
      self.M.P.write(param_i, abs_jdir)
      self.M.P.write_json(param_i, abs_jdir)
      self.M.evaluate(param_i)

      # update object being returned
      params_hash = jdir
      tasks_run.update( {params_hash: [list(param_i), relative_jdir]} )

      # update ParametricScheduler.cache
      stat = self.M.exec_status()
      self.cache_insert(param_i, params_hash, relative_jdir, stat)

      self.M.finalize()
  
    return tasks_run


  def schedule(self, params, force=False):
    if not force:
      to_eval, run, ignore = self.filter_run_ignore_from_cache(params)
      params_eval = np.array(params[to_eval, :])
      tasks_run = self.run_jobs(params_eval)
    else:
      tasks_run = self.run_jobs(params)
      run = dict(tasks_run)
      ignore = dict() # empty - everything was run
    return run, ignore


  def schedule_from_csv(self, fname):
    data = np.genfromtxt(fname, comments="#", delimiter=" ")
    print(data, data.dtype)
    # check data matches model parameter definition
    n_jobs, n_inputs = data.shape[0], data.shape[1]
    if n_inputs != self.P.n_inputs:
      print(self.P)
      raise ValueError('Inputs parsed from ' + fname + ' are inconsistent with parameter defitinion. Found ' + str(n_inputs) + ' input parameters.')
    
    run, ignore = self.schedule(data, force=False)
    return run, ignore


  def batched_schedule(self, params, max_jobs=1, wait_time=60.0, force=False):

    udef = dict(self.cache[status.UNDEFINED])
    L = len(udef)
    print('iteration[init]', 'len(UDEF)', L)
    s = 0
    e = min( max_jobs - L, len(params) )
    _params = np.array(params) # copy
    its = 1
    while len(_params) != 0:
      print('s', s, 'e', e)
      _p = _params[s:e, :]
      print(_p)
      _params = np.array(_params[e:, :])
      self.schedule(_p)
      udef = dict(self.cache[status.UNDEFINED])
      L = len(udef)
      print('iteration', its, 'len(UDEF)', L)
      while L >= max_jobs:
        self.probe(wait_time)
        udef = dict(self.cache[status.UNDEFINED])
        L = len(udef)
      s = 0
      e = min( max_jobs - L, len(_params) )
      its += 1
    
    return None, None


  def wait_all(self, wait_time=60.0):
    udef = dict(self.cache[status.UNDEFINED])
    L = len(udef)
    count = 0
    while L != 0:
      self.probe(wait_time)
      udef = dict(self.cache[status.UNDEFINED])
      L = len(udef)
      count += 1
    return count


  @classmethod
  def collect_valid_trajectories(cls, pathname):
    
    found = os.path.exists(pathname)
    if not found:
      raise RuntimeError( pathname + ' does not exist')
    
    # Look for a definition file
    pdef = ParametricInput(os.path.join(pathname, 'parametric_def.csv'))
    
    phash = pdef.generate_phash()
    
    # Collect directory names
    # (i) Scan each directory; (ii) Look for param file; (iii) Validate observable
    hash_list = []
    param_dir_list = []
    
    hash_list_invalid = []
    param_dir_list_invalid = []

    # walk directories recursively
    ndirs = 0
    for dirpath, dirs, files in os.walk(pathname):
      #print(dirpath, dirs, files)
      # look for existence of 'params.csv' indicating a job was run
      if 'params.json' in files:
        is_valid = pdef.validate_from_file(phash, dirpath)
        p = pdef.read_json(dirpath)
        values = list(p.values())
        hidx = pdef.get_identifier(values)

        if is_valid:
          hash_list.append(hidx)
          param_dir_list.append([values, dirpath])
        else:
          hash_list_invalid.append(hidx)
          param_dir_list_invalid.append([values, dirpath])
    
      ndirs += len(dirs)
    #print('d', dlist)

    print('processed', str(ndirs), 'directories > validated',  str(len(hash_list)), 'directories')
    print('directories processed:', str(len(hash_list) + len(hash_list_invalid)))
    print('directories containing valid models:', str(len(hash_list)))
    print('directories containing invalid models:', str(len(hash_list_invalid)))
    for k in range(len(hash_list_invalid)):
      print('  ' + str(hash_list_invalid[k]) + ' -> ' + param_dir_list_invalid[k][1])
    
    return dict(zip(hash_list, param_dir_list))


  @classmethod
  def group_trajectories(cls, valid, model):
    """
    Create a dict with three keys for successful, failed and undefined jobs.
    `valid` is returned from collect_valid_trajectories()
    """
    
    def get(model, job):
      model.output_path = job[1]
      model.initialize()
      st = model.exec_status()
      model.finalize()
      return st
  
    def dict_pretty_print(d, dname, indent=0):
      kk, vv = list(d.keys()), list(d.values())
      nitems = len(kk)
      if nitems == 0: return
      print(indent * '  ' + '--- ' + dname + ' ---')
      print(indent * '  ' + 'param hash | params | output path')
      for i in range(nitems):
        line = (indent+1) * '  ' + str(kk[i]) + ' | ' + str(vv[i][0]) + ' | ' + str(vv[i][1])
        print(line)

    #successful = {  key: model.exec_status()  for key, value in valid  }
    #for key, value in valid.items():
    #  print(get(model, value))

    # collect status for every valid job
    stats = [ get(model, value)  for (key, value) in valid.items() ]
    
    # create dict of param-hash: status pairs
    all = dict( zip( list(valid.keys()), stats) )
    #print('all', all)
    
    # filter param-hash: [param values, absolute-path-to-output] for successful jobs
    success = {  key: valid[key] for (key, value) in all.items()  if value == status.SUCCESS }
    dict_pretty_print(success, 'job.status = success')

    error = {  key: valid[key] for (key, value) in all.items()  if value == status.ERROR }
    dict_pretty_print(error, 'job.status = error')

    undef = {  key: valid[key] for (key, value) in all.items()  if value == status.UNDEFINED }
    dict_pretty_print(undef, 'job.status = undefined')

    cache = { status.SUCCESS: success, status.ERROR: error, status.UNDEFINED: undef }
    return cache


  def cache_insert(self, params, params_hash, jobpath, stat):
    p = self.P._convert(params)
    values = list(p.values())
    #hidx = self.P.get_identifier(values)

    jlist = self.cache[stat] # shallow copy (reference dict)
    new_data = { params_hash: [params, jobpath] }
    jlist.update(new_data)


  def cache_update_all(self):
    """
    Check that everything in the cached ERROR and UNDEFINED dict are still in those slots.
    If not, move these jobs
    """
    
    D = dict( self.cache[status.ERROR] )
    for (key, jvals) in D.items():
      params_hash = key
      relative_jdir = jvals[1]
      param_i = jvals[0]

      abs_jdir = os.path.abspath(relative_jdir)
      self.M.output_path = abs_jdir
      self.M.initialize()
      stat = self.M.exec_status()
      self.M.finalize()
      
      if stat != status.ERROR:
        ierr = self.cache[status.ERROR].pop(key)
        self.cache_insert(param_i, params_hash, relative_jdir, stat)

    D = dict( self.cache[status.UNDEFINED] )
    for (key, jvals) in D.items():
      params_hash = key
      relative_jdir = jvals[1]
      param_i = jvals[0]
      
      abs_jdir = os.path.abspath(relative_jdir)
      self.M.output_path = abs_jdir
      self.M.initialize()
      stat = self.M.exec_status()
      self.M.finalize()
      
      if stat != status.UNDEFINED:
        ierr = self.cache[status.UNDEFINED].pop(key)
        self.cache_insert(param_i, params_hash, relative_jdir, stat)


  def get_new_jobs(self):
    r = dict(self.cache[status.ERROR])
    return r


  def get_ignored_jobs(self):
    r = dict(self.cache[status.SUCCESS])
    r.update(self.cache[status.UNDEFINED])
    return r


  def probe(self, wait=2.0):
    """
    Sleep for `wait` seconds and then update the cache.
    Return:
    - Number of new jobs found with exec_status() = SUCCESS after
    waiting for `wait` seconds.
    """
    jobs_init = len( self.cache[status.SUCCESS] )
    time.sleep(wait)
    self.cache_update_all()
    
    jobs_final = len( self.cache[status.SUCCESS] )
    return jobs_final - jobs_init


  def flush(self):
    """
    Run all cached jobs with exec_status = ERROR.
    """
    jobs_init = len( self.cache[status.SUCCESS] )
    
    D = dict( self.cache[status.ERROR] )
    for (key, jvals) in D.items():
      params_hash = key
      relative_jdir = jvals[1]
      param_i = jvals[0]
      
      abs_jdir = os.path.abspath(relative_jdir)
      self.M.output_path = abs_jdir
      self.M.initialize()
      self.M.evaluate(param_i)
      stat = self.M.exec_status()
      self.M.finalize()
      
      if stat != status.ERROR:
        ierr = self.cache[status.ERROR].pop(key)
        self.cache_insert(param_i, params_hash, relative_jdir, stat)

    jobs_final = len( self.cache[status.SUCCESS] )
    return jobs_final - jobs_init


  def cache_generate_log(self, logfname='jobs_log.csv', jstatus=status.SUCCESS):
    import csv
 
    pathname = self.root_dir
    with open(logfname, "w") as fp:
      # using csv.writer method from CSV package
      write = csv.writer(fp)

      # insert comments
      fp.write('# valid parametric jobs' + '\n')
      fp.write('# root directory: ' + pathname + '\n')
    
      pdef = self.P
      pd = "# " + str(pdef)
      pd = pd.replace("\n","\n# ")
      fp.write(pd + '\n')
      
      # insert header
      header = [ n for n in pdef.param_names ]
      header.append('path')
      header.append('identifier')
      
      write.writerow(header)

      # generate contents
      _csv = []
      dlist = self.cache[jstatus]
      #print(dlist)
      for (key, values) in dlist.items():
        row = list(values[0])
        row.append(values[1])
        row.append(key)
        _csv.append(row)
      write.writerows(_csv)


  @classmethod
  def generate_log(cls, pathname, logfname='jobs_log.csv', model=None):
    
    found = os.path.exists(pathname)
    if not found:
      raise RuntimeError( pathname + ' does not exist')

    # Look for a definition file
    pdef = ParametricInput(os.path.join(pathname, 'parametric_def.csv'))

    phash = pdef.generate_phash()

    #print('start')
    # Collect directory names
    # (i) Scan each directory; (ii) Look for param file; (iii) Validate observable
    dlist = []
    # walk directories recursively
    ndirs = 0
    for dirpath, dirs, files in os.walk(pathname):
      #print(dirpath, dirs, files)
      # look for existence of 'params.csv' indicating a job was run
      if 'params.csv' in files:
        is_valid = pdef.validate_from_file(phash, dirpath)
        if is_valid:
          dlist.append(dirpath)
      if len(dirs) == 0:
        ndirs += 1
    #print('d', dlist)
    #print('end')
    print('processed', str(ndirs), 'directories > validated',  str(len(dlist)), 'directories')

    """
    _csv = []
    header = [ n for n in pdef.param_names ]
    header.append("path")
    header.append("identifier")
    _csv.append(header)
    print(header)
    for d in dlist:
      names, values = pdef.read(d)
      row = list(values)
      row.append(d)
      p = pdef._convert(values)
      h = pdef.get_identifier(values)
      row.append(h)
      print(row)
      _csv.append(row)
    np.savetxt(logfname, _csv, delimiter=" ", fmt="%s")
    """

    import csv

    with open(logfname, "w") as fp:
      # using csv.writer method from CSV package
      write = csv.writer(fp)

      # insert comments
      fp.write('# valid parametric jobs' + '\n')
      fp.write('# root directory: ' + pathname + '\n')

      pd = "# " + str(pdef)
      pd = pd.replace("\n","\n# ")
      fp.write(pd + '\n')

      # insert header
      header = [ n for n in pdef.param_names ]
      header.append('path')
      header.append('identifier')

      write.writerow(header)

      # generate contents
      _csv = []
      for d in dlist:
        
        names, values = pdef.read(d)
        row = list(values)
        row.append(d)
        p = pdef._convert(values)
        h = pdef.get_identifier(values)
        row.append(h)
        #print(row)
        _csv.append(row)
        
        """
        p = pdef.read_json(d)
        values = list(p.values())
        row = list(values)
        row.append(d)
        h = pdef.get_identifier(p)
        row.append(h)
        _csv.append(row)
        """
      write.writerows(_csv)