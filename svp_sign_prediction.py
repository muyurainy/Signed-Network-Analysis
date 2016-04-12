#Contains methods for sign prediction in signed networks
#Based on Chiang et. al, 2014

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from scipy.linalg import norm

#Input: adjacency matrix with signs as entries
# Rank (max rank of solution before taking sign matrix)
# Tolerance (how close does solution need to be to stop iterating)
# Maximum number of iterations
# Step size: how fast to update solution
# Mode: normal or test mode to perform additional tests

#Output: signed version low rank matrix that approximately solves
# sign prediction optimization problem
#NOTE: signed version is probably not low rank
#TODO write more official tests
def sign_prediction_SVP(adj_matrix, 
                        rank, 
                        tol, 
                        max_iter,
                        step_size,
                        mode = "normal"):

  #Initialization
  num_iters = 0
  solution = csr_matrix(np.zeros(adj_matrix.shape)) #matrix of zeros

  #Iterate until tolerance level or maximum # iters is reached
  while num_iters <= max_iter and not within_tol(
                                        solution, adj_matrix, tol):
    #update
    solution = solution - step_size*(projection(
                          solution, adj_matrix.nonzero()) - adj_matrix)
    #compute top <rank> SVs
    left_svecs, svals, right_svecs = svds(solution, k = rank)
    
    #form low rank approximation
    solution = csr_matrix(np.dot(np.dot(left_svecs, np.diag(svals)), right_svecs))
    num_iters += 1

  #confirm that solution (before signing, which will change things) is desired rank
  if mode == "test":
    assert np.linalg.matrix_rank(np.asarray(solution.todense())) == rank

  return csr_matrix.sign(solution) #recall we want signs (edge sign predictions)

#Input: "solution" of SVP, adjacency matrix, tolerance
#Output: boolean reflecting whether or not
# projection of solution (onto nonzero elements of adj matrix)
# is "tolerably" close to adjacency matrix
def within_tol(solution, adj_matrix, tol):
  proj = projection(solution, adj_matrix.nonzero())
  diff = proj - adj_matrix
  try:
    return norm(diff.A, "fro") < tol #.A gets nonzero entries of sparse matrix
  except ValueError:
    print("%d NaNs in solution" % np.any(np.isnan(solution)))

#Input: matrix to project
#Tuple of rows and columns that can be nonzero in projection
#Output: projection (make unobserved indices zero, keep observed indices)
def projection(matrix, observed_indices):
  proj = csr_matrix(np.zeros(matrix.shape)) #matrix of zeros

  #fill in with projected values
  proj[observed_indices] = matrix[observed_indices] 
  return proj
