from distutils import errors
import numpy as np

class NewtonRaphson:
    def __init__( self, x, K, a, b, epsilon ):
        """

        Parameters:
        -----------
            x : ndarray, (n+m,)
                The vector containing  u =exp(f/epsilon) and v = exp(g/epsilon), where f and g are Kantorovich potentials.    
            K : ndarray, shape (n,m)
                The Gibb's kernel.
            a : ndarray, shape (n,)
                The probability histogram of the sample of size n.
            b : ndarray, shape (m,)
                The probability histogram of the sample of size m.
            epsilon : float
                      The regularization factor in the entropy regularized optimization setup of the optimal transport problem.
        """
        self.x = x
        self.K = K
        self.a = a
        self.b = b
        self.N1 = a.shape[0]
        self.N2 = b.shape[0]
        self.epsilon = epsilon
        self.err_a = []
        self.err_b = []
    
    def _func_phi( self ):
        y = np.exp( self.x/self.epsilon )
        u = y[:self.N1]
        v = y[self.N1:]
        r1 = np.dot( np.dot( np.diag( u ), self.K ), v )
        r2 = np.dot( np.dot( np.diag(v), self.K.T ), u )
        return np.hstack( ( r1 - self.a, r2 - self.b ) )

    def _func_jacobian( self, debug = False ):
        """

        Parameters:
        -----------
            debug : bool 
                    To understand the condition number of the Hessian. Defaults to False.

        Returns:
        --------
            result_stabilized : ndarray, shape (n,m)
                                The stabilized Hessian.
        """
        eig_vector = np.hstack( ( np.ones( self.N1 ), - np.ones( self.N2 ) ) )/np.sqrt( self.N1 + self.N2 )
        eig_vector = np.reshape( eig_vector, ( self.N1 + self.N2, 1 ) )

        y = np.exp( self.x/self.epsilon )
        u = y[ : self.N1 ]
        v = y[ self.N1 : ]
        #
        r1 = np.dot( np.dot( np.diag( u ), self.K ), v )
        r2 = np.dot( np.dot( np.diag( v ), self.K.T ), u )
        P  = np.dot( np.dot( np.diag( u ), self.K ), np.diag( v ) )
        # Form matrix 
        # [ A,B
        #   C,D ]
        # = 
        # [ diag(r1),P
        #   P.T,diag(r2) ]    
        A = np.diag( r1 )
        B = P
        C = P.T
        D = np.diag( r2 )
        result = -np.vstack( ( np.hstack( ( A, B ) ), np.hstack( ( C, D ) ) ) )/self.epsilon
        
        
        # Inflating the corresponding direction
        mean_eig = 0.5 * np.mean( r1 ) + 0.5 * np.mean( r2 )
        result_stabilized = result + mean_eig * np.dot( eig_vector, eig_vector.T )
        # Conjecture: Smallest eigenvalue in absolute value has eigenvector approx (\mathds{1}_n, -\mathds{1}_m)
        if debug:
            def print_spectral_statistics( mat ):
                eig, v = np.linalg.eig( mat )
                sorting_indices = np.argsort( eig )
                eig = eig[ sorting_indices ]
                v   = v[ :, sorting_indices ]
                print( "Mean eigenvalue: ", np.mean( eig ) )
                print( "List of smallest eigenvalues: ", eig[ : 10 ] )
                print( "List of largest  eigenvalues: ", eig[ - 10 : ] )
                min_index = np.argmin( np.abs( eig ) )
                max_index = np.argmax( np.abs(eig) )
                min_value = eig[ min_index ]
                max_value = eig[ max_index ]
                min_vector = v[ :, min_index ]
                min_vector = min_vector/min_vector[0]
                max_vector = v[ :,max_index ]
                max_vector = max_vector/max_vector[0]
                condition_number = max_value/min_value
                #print( "Min eigenvalue vector: ", max_vector)
                #
                #print( v[:,0]*np.sqrt( self.N1 + self.N2))
                #vector = v[:,0]
                #test = np.dot( result, vector)
                #print( np.linalg.norm(test) )
                #print("Min absolute eigenvalues: ", min_value)
                #print("Norm of v-1: ", np.linalg.norm(min_vector-eig_vector))
                print( "Condtion number: ", condition_number )
            # end def

            print( "Raw eig:" )
            print_spectral_statistics( result )            
            print("")

            print( "Regularized eig:" )
            print_spectral_statistics( result_stabilized )            
            print("")
        return result_stabilized
    
    def _update( self, maxiter = 200, tol = 1e-15, debug = False ):
        """

        Parameters:
        -----------
            tol : float
                  The tolerance limit for the error. Defaults to 1e-15.
            maxiter : int 
                      The maximum iteration for the optimization algorithm. Defaults to 200.
            debug : bool 
                    To understand the condition number of the Hessian. Defaults to False.

        Returns:
        --------
        Returns a dictionary where the keys are strings and the values are ndarrays.
        The following are the keys of the dictionary and the descriptions of their values:
            error_a : ndarray, shape (k,), where k is the number of iterations
                  The list of error of the estimation of the measure 'a' over the iteration of the algorithm.
            error_b : ndarray, shape (k,), where k is the number of iterations
                  The list of error of the estimation of the measure 'b' over the iteration of the algorithm.

        """
        i = 0 
        while True:
            target   = self._func_phi()
            jacobian = self._func_jacobian( debug )
            e = [ np.linalg.norm( target[:self.N1] ), np.linalg.norm( target[self.N1:] ) ]
            self.x   = self.x + np.linalg.solve( jacobian, target )
            # Matrix inversion
            # inv_jac  = np.linalg.inv( jacobian)
            # x = x - np.dot( inv_jac, target )
            self.err_a.append( e[0] )
            self.err_b.append( e[1] )

            iter_condition = ( e[0] > tol or e[1] > tol )
            if iter_condition and i < maxiter:
                i += 1
            else:
                print( "Terminating after iteration: ", i )
                break 
        return {
            'error_a' : self.err_a,
            'error_b' : self.err_b,
        }

