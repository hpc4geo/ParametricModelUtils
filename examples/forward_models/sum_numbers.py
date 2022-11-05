
import sys
import numpy as np

if __name__ == "__main__":
  args = sys.argv[1:]
  nums = np.array(args, dtype=np.float64)
  val = np.sum(nums)
  with open('obs.txt', 'w') as fp:
    fp.write(str(val))

