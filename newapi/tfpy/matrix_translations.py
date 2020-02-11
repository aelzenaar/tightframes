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
  matrix_rows = '['
  for i in range(0,self.d):
      for j in range(0,self.n):
          matrix_rows = matrix_rows + f'    {self.matrix[i][j]:.{accuracy}}'
          if not ((i == self.d - 1) and (j == self.n - 1)):
              matrix_rows = matrix_rows + ',\n'
  matrix_rows = matrix_rows + '\n]'
  return matrix_rows
