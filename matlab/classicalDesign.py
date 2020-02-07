from itertools import chain, combinations
from math import comb

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


class FDError(Exception):
  pass

class DimensionError(FDError):
  """Exception raised for incorrect number of dimensions of object passed in,
     or non-square object.
  """
  pass


def classicalDesignMatlab(mA,tolerance):
  """Decide whether the design represented by the Gramian mA
     is a classical t-(v,k,λ) design, up to sign of entries,
     comparing entries up to tolerance.

  Arguments:
      mA -- memoryview object of two dimensions, representing the matrix.
      tolerance -- the number of decimal places to compare.
  """
  if mA.ndim != 2 or mA.shape[0] != mA.shape[1]:
    raise DimensionError()

  A = mA.cast('d',mA.shape)

  return classicalDesign(A,tolerance)

def classicalDesign(A, tolerance):
  """Decide whether the design represented by the Gramian mA
     is a classical t-(v,k,λ) design, up to sign of entries,
     comparing entries up to tolerance.

  Arguments:
      A -- list object of two dimensions, representing the matrix.
      tolerance -- the number of decimal places to compare.
  """

  dim = len(A)

  D = {}

  for i in range(0,dim):
    for j in range(0,dim):
      if i == j:
        continue

      entry = round(A[i][j],tolerance)
      if entry not in D:
        D[entry] = set()
      D[entry] = D[entry] | {i,j}

  b = len(D)
  print(f'Blocks: {D}')
  print(f'Block count: {b}')

  blockSizes = set()
  for block in D:
    blockSizes = blockSizes | {len(D[block])}
    print(blockSizes)
  if len(blockSizes) > 1:
    print(f'The block size is not constant.')
    return None
  k = blockSizes.pop()
  print(f'Block size: {k}')

  varieties = set(*[D[b] for b in D])
  print(f'Varieties: {varieties}')
  v = len(varieties)

  for t in range(1,k+1):
    # Compute the corresponding value of λ.
    λ = (comb(v,t))/(b*comb(k,t))
    print(f'Checking t = {t}, λ = {λ}...')

    # Check whether each t-subset lies in exactly λ blocks.
    counts = set()
    for subset in powerset(varieties):
      if len(subset) != t:
        continue

      count = 0
      s = set(subset)
      for block in [D[b] for b in D]:
        if s <= block:
          count = count + 1
      print(f'{t}-subset {s} lies in {count} blocks.')
      counts = counts | {count}
    if len(counts) == 1 or counts.pop() == λ:
      print(f'The matrix forms a {t}-({v},{k},{λ}) design.')
      return (t,v,k,λ)
    else:
      print(f'The matrix does not form a {t}-({v},{k},{λ}) design. Possible counts for different subsets were {counts}.')

  return None
