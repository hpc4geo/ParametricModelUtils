
import sys, time
import numpy as np

if __name__ == "__main__":
  with open('sum_numbers.start', 'w') as fp:
    fp.write('')
  time.sleep(20.0)
  args = sys.argv[1:]
  nums = np.array(args, dtype=np.float64)
  print('x', nums)
  val = np.sum(nums)
  with open('obs.txt', 'w') as fp:
    fp.write(str(val))


  #a = None
  #a += 1

