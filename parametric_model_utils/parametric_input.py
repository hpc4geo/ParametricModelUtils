
import os
from collections import OrderedDict
import hashlib
import csv as csv
import json as json
import numpy as np

class ParametricInput:
  
  
  def _parse(self, inputfile):
    """
    Load a CSV file defining the following quantities
    parameter name, lower bound, upper bound, unit.
    _parse() defines and initializes the class attributes
      `.param_names` (list)
      `.param_bounds` (OrderedDict)
      `.param_units` (OrderedDict)
      `.param_bounds` and `.param_units` have keys which are given
    by each element of `.param_names`.
    """
    data = np.genfromtxt(inputfile, comments="#", delimiter=" ", dtype=str)
    data = np.atleast_2d(data)

    keys = data[:,0]
    self.param_names = list(keys)
    
    self.param_bounds = OrderedDict()
    self.param_units = OrderedDict()
    i = 0
    for k in keys:
      self.param_bounds[k] = (float(data[i,1]), float(data[i,2]))
      unit = data[i,3]
      self.param_units[k] = unit.replace('"','')
      i += 1

  def __init__(self, inputfile, _params=None, hash_paths=True):
    """
    Example usage
      `
      parameter = ParametricInput( 'input.csv' )
      parameter = ParametricInput( None, _params=[ {"name": "vx", "bounds":[0,1.0], "units":"m/s"},
                                                   {"name": "eta", "bounds":[0,1.0e4], "units":"Pas"} ] )
      `
    """
    self.hash_paths = hash_paths
    
    self.param_names = list()
    self.param_bounds = OrderedDict()
    self.param_units = OrderedDict()
    
    if inputfile is not None: # from file
      self._parse(inputfile)
    else: # build from input dict
      self.param_names, bb, uu = list(), list(), list()
      for pn in _params:
        self.param_names.append( pn["name"] )
        bb.append( pn["bounds"] )
        uu.append( pn["units"] )
      self.param_bounds = OrderedDict( zip(self.param_names, bb) )
      self.param_units = OrderedDict( zip(self.param_names, uu) )
      
    self.n_inputs = len(self.param_names)
    self.phash = self.generate_phash()


  def _is_singleton(self, p):
    """
    Check if p defines a single parameter set.
    """
    if not isinstance(p, OrderedDict):
      raise RuntimeError('Only valid if input is an OrderedDict')
    is_single = True
    for n in self.param_names:
      vals = p[n]
      try:
        iterable = iter(vals)
        is_single = False
        break
      except:
        pass
    return is_single


  def _convert(self, params):
    if isinstance(params, (dict, OrderedDict)):
      p = OrderedDict()
      for k in self.param_names:
        p[k] = params[k]
      return p
    
    elif isinstance(params, np.ndarray):
      if params.ndim == 1:
        if len(self.param_names) != params.shape[0]:
          raise ValueError('`params` is the wrong size')
        p = OrderedDict( zip(self.param_names, params)  )

      elif params.ndim == 2:
        p = OrderedDict()
        for k in range(self.n_inputs):
          p[self.param_names[k]] = params[:, k]

      else:
        raise ValueError('`params` must be 1-D (nparam) or 2-D (n x nparam) ndarray')

      return p
        
    elif isinstance(params, list):
      
      if not isinstance(params[0], list):
        if len(self.param_names) != len(params):
          raise ValueError('`params` is the wrong size')
      
        p = OrderedDict( zip(self.param_names, params)  )
      elif isinstance(params[0], list):
        # convert to ndarray
        params_1 = np.array(params, dtype=np.float64)
        print(params_1)
        p = self._convert(params_1)
      return p
    else:
      raise ValueError('`params` type is not supported')


  # hash(paramname1__paramvalue1__paramname2_paramvalue2__...
  def get_identifier(self, params):
    """
    Convert `params` into a unique identifier.
    """
    p = self._convert(params)
    if not self._is_singleton(p):
      raise RuntimeError('Only valid for singleton parameter')
    
    keys = list(p.keys())
    vals = list(p.values())
    vals = [ str(v) for v in vals ] # flatten into strings
    pval = [ keys[i]+"_"+vals[i] for i in range(len(keys)) ] # merge each key-val pair seperated with single underscore
    param_val = "__".join(pval) # merge all key-val pairs seperated with double underscore
    #print('[+] key_value pairs', param_val)
    
    if self.hash_paths == True:
      #print('[+] Hashing parametric job ouput directory name')
      b = param_val.encode()
      key_hash = hashlib.sha1(b).hexdigest()
      idenifier = key_hash
    else:
      idenifier = param_val

    return idenifier


  def get_identifiers(self, params):
    """
    Convert `params` into a unique identifier.
    """
    p = self._convert(params)
    keys = list(p.keys())
    # To ensure correct functionality with params being a list [[x,y],[w,z]] or an ndarray
    # we convert the values via _convert() and then stack values into an ndarray
    _vals = list(p.values())
    _params = np.vstack(_vals).T # Get list of np.array and pack it into an np.ndarray for slicing
    idenifier = list()
    for i in range(_params.shape[0]):
      vals = _params[i, :]
      vals = [ str(v) for v in vals ] # flatten into strings
      pval = [ keys[i]+"_"+vals[i] for i in range(len(keys)) ] # merge each key-val pair seperated with single underscore
      param_val = "__".join(pval) # merge all key-val pairs seperated with double underscore
      idenifier.append(param_val)
    if self.hash_paths == True:
      for pv in idenifier:
        b = pv.encode()
        key_hash = hashlib.sha1(b).hexdigest()
        idenifier[ idenifier.index(pv) ] = key_hash
    
    return idenifier


  def write(self, params, output_path=""):
    """
    Write `params` to a CSV file named `params.csv`.
    """
    p = self._convert(params)
    if not self._is_singleton(p):
      raise RuntimeError('Only valid for singleton parameter')
    
    keys = np.array( list(p.keys()) )
    vals = list(p.values())
    vals = [ str(v) for v in vals ] # flatten into strings
    vals = np.array( vals )
    units = np.array( list(self.param_units.values()), dtype=str )
    #data = np.vstack([keys, vals, units])
    data = np.vstack([keys, vals])
    
    np.savetxt(os.path.join(output_path, 'params.csv'), data.T, delimiter=" ", fmt="%s")

    self.write_phash(output_path)


  def read(self, output_path=""):
    """
    Read `params.csv`. 
    
    Returns 
    `data[:, 0]`: np.ndarray
      - Parameter names
    `np.array(vals)`:  np.ndarray
      - Parameter values
    """
    fname = os.path.join(output_path, 'params.csv')
    fp = open(fname, "r")
    data = np.loadtxt(fname, comments="#", delimiter=" ", dtype=str)
    fp.close()
    #print(data)
    vals = [ float(x) for x in data[:, 1]]
    return data[:, 0], np.array(vals)


  def write_json(self, params, output_path=""):
    p = self._convert(params)
    if not self._is_singleton(p):
      raise RuntimeError('Only valid for singleton parameter')
    input = json.dumps(p)
    fname = os.path.join(output_path, 'params.json')
    with open(fname, "w") as fp:
      fp.write(input)

    self.write_phash(output_path)


  def read_json(self, output_path=""):
    fname = os.path.join(output_path, 'params.json')
    with open(fname, "r") as fp:
      input = fp.read()
      p = OrderedDict(json.loads(input))
    #p = self._convert(p) # if we want to ensure the ordering is always consistent
    return p


  def create_database_record(self, params):
    """
    Prepare a collection of strings which can be written to a CSV file that describes the
    parameters defined by `params`.
    
    Returns list of strings.
    """
    p = self._convert(params)
    if not self._is_singleton(p):
      raise RuntimeError('Only valid for singleton parameter')
    
    row_values = list(p.values())
    row_values = [ str(v) for v in row_values ] # flatten into strings
    d = self.get_identifier(p)
    row_values.append(d)
    return row_values


  def generate_phash(self):
    pkey = ["_"]
    pkey += [ k + "_" for k in self.param_names ]
    pkey = "".join(pkey)
    return pkey


  def write_phash(self, output_path=""):
    fname = os.path.join(output_path, 'parametric_def.hash')
    fp = open(fname, "w")
    pkey = self.generate_phash()
    fp.write(pkey)
    fp.close()


  # param_name min_value max_value units
  def write_definition(self, output_path=""):
    """
    Writes a CSV description of the parameter definition that was parsed by the class constructor.
    """
    fname = os.path.join(output_path, 'parametric_def.csv')
    fp = open(fname, "w")
    fp.write('# param_name min_value max_value units'+'\n')
    for i in range(len(self.param_names)):
      key = self.param_names[i]
      line = " ".join([self.param_names[i], str(self.param_bounds[key][0]), str(self.param_bounds[key][1]), self.param_units[key]]) + '\n'
      fp.write(line)
    fp.close()

    self.write_phash(output_path)


  def __str__(self):
    view = 'ParametricInput:' + '\n'
    for k in range(self.n_inputs-1):
      view += '  ' + ('%12s' % self.param_names[k]) \
              + (' [%6s]' % self.param_units[self.param_names[k]]) \
              + (' <%+1.4e , %+1.4e>' % (self.param_bounds[self.param_names[k]][0],self.param_bounds[self.param_names[k]][1]) ) \
              + '\n'
    view += '  ' + ('%12s' % self.param_names[-1]) \
                 + (' [%6s]' % self.param_units[self.param_names[-1]]) \
                 + (' <%+1.4e , %+1.4e>' % (self.param_bounds[self.param_names[-1]][0],self.param_bounds[self.param_names[-1]][1]) )
    return view


  def validate_from_file(self, phash, pathname):
    """
    Load `parametric_def.hash`, and check it is identical (i.e. consistent)
    with definition of the parameters given by `phash`.
    """
    fname = os.path.join(pathname, 'parametric_def.hash')
    try:
      fp = open(fname, "r")
      phash_c = fp.read()
      fp.close()
      if phash == phash_c:
        return True
      else:
        return False
    except:
      return False


  def compare(self, x):
    if self.phash == x.phash: return True
    else:                     return False
