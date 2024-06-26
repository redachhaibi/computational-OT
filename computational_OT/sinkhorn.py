import numpy as np

class Sinkhorn:

  def __init__(self,K,a,b,u,v,epsilon):
    self.K = K
    self.a = a
    self.b = b
    self.u = u
    self.v = v
    self.epsilon = epsilon
    self.err_a = []
    self.err_b = []
    self.obj = []
    
  def _objectivefunction(self):
        """Computes the value of the objective function at x"""
        f = np.log(self.u)*self.epsilon
        g = np.log(self.v)*self.epsilon
        target = np.dot(f.T,self.a)+np.dot(g.T,self.b)
        penalization = -self.epsilon*np.dot(np.exp(f/self.epsilon).T,np.dot(self.K,np.exp(g/self.epsilon)))
        return target+ penalization


  def _update(self, tol=1e-12, maxiter=1000):
    i = 0
    while True :
      self.obj.append(self._objectivefunction())

      # sinkhorn step 1
      self.u = self.a / np.dot( self.K, self.v )
      # error computation 1
      r = self.v*np.dot( self.K.T, self.u)
      self.err_b.append(np.linalg.norm(r - self.b))
      
      # sinkhorn step 2
      self.v = self.b / np.dot( self.K.T, self.u )
      
      # error computation 2
      s = self.u*np.dot( self.K, self.v )
      self.err_a.append(np.linalg.norm(s - self.a))
      iter_condition = (self.err_a[-1]>tol or self.err_b[-1]>tol)
      if iter_condition and i<maxiter :
          i += 1
      elif np.isnan(self.err_a[-1]) or np.isnan(self.err_b[-1]):
        print("Sinkhorn is unstable for epsilon: ", self.epsilon, " as there occurs divison by exponentially small values while performing the alternative projection. ")
        break
      else:
        print("Terminating after iteration: ",i)
        break   

    # end for
    return {
      'potential_f' : self.epsilon*np.log(self.u).reshape(self.a.shape[0],),
      'potential_g' : self.epsilon*np.log(self.v).reshape(self.b.shape[0],),
      'error_a'     : self.err_a,
      'error_b'     : self.err_b,
      'objectives'  : self.obj
    }
