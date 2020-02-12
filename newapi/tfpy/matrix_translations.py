import numpy

def array_to_matlab(array, accuracy = 32):
  string = "["
  for row in array:
    for cell in row:
      string = string + str(cell) + ','
    string = string[:-1] # Remove trailing comma at end of row
    string = string + ';\n '
  string = string + ']'
  return string

def array_to_magma(array, accuracy = 32):
  d = array.shape[0]
  n = array.shape[1]
  matrix_rows = '['
  for i in range(0,d):
      for j in range(0,n):
          matrix_rows = matrix_rows + f'    {array[i][j]:.{accuracy}}'
          if not ((i == d - 1) and (j == n - 1)):
              matrix_rows = matrix_rows + ',\n'
  matrix_rows = matrix_rows + '\n]'
  return matrix_rows
