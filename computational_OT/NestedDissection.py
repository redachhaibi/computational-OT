import numpy as np
import matplotlib.pyplot as plt
import sys
class NestedDissection:

    def __init__( self, P, stopdim = 2 ):
        """

        Parameters:
        -----------
            P : ndarray, shape (n,m)
                The coupling of the probability histograms of size n and m.
        """

        self.P = P
        self.stopdim = stopdim
        

    def _nd( self, x = None ):
        
        if x is not None:
            mat = x
            if x.shape is not ():
                m,n = mat.shape[0], mat.shape[1]
                max = np.max( [ m, n ] )
            
        else:
        
            mat = self.P.reshape( self.P.shape[0], -1 )
            m, n = mat.shape[0], mat.shape[1]
            max = np.max( [ m, n ] )
           
      
            
        if max <= self.stopdim:

            return mat[:,:]

        
        # if m>=max:
        # if m>=max and n>=max:

        #     p=np.zeros((m,n))
        #     s = (m//2)
        #     middle1= mat[s-1,:]
        
        #     p[:s-1,:]=self._nd(mat[:s-1,:])
        #     p[s-1:m-1,:]=self._nd(mat[s:,:])
        #     p[m-1,:]=middle1

        #     k=(n//2)
        #     middle2 = p[:,s-1]
        #     p[:,:s-1]=self._nd(p[:,:s-1])
        #     p[:,s-1:n-1]=self._nd(p[:,s:])
        #     p[:,n-1]=middle2
   
            
        # else:
        if m >= max:
            p = np.zeros( ( m, n ) )
            s = ( m//2 )
            middle = mat[s-1,:]
        
            p[:s-1,:] = self._nd(mat[:s-1,:])
            p[s-1:m-1,:] = self._nd(mat[s:,:])
            p[m-1,:] = middle
    
        if n >= max:
            p = np.zeros( ( m, n ) )
            s = ( n//2 )
            middle = mat[:,s-1]
            p[:,:s-1] = self._nd(mat[:,:s-1])
            p[:,s-1:n-1] = self._nd(mat[:,s:])
            p[:,n-1] = middle
        
        return p
               
      

    def _evaluate( self, cutoffx = 0, cutoffy = 0, epsilon = 0, index = 0 ):
        """

        Parameters:
        -----------
            cut_offx :  int . Defaults to 0.
                        Cutoff on the matrix P_xx = PP^{T}.

            cut_offy :  int . Defaults to 0.
                        Cutoff on the matrix P_yy = P^{T}P.

            epsilon  :  int . Defaults to 0.
                        The regularizing factor of the regularization in the objective function.
            index    :  int . Defaults to 0.
                        The index i corresponds to the experiment and its outputs using the epsilon at the index i in the list of epsilons. 
        """
        sys.setrecursionlimit( 100000 )

        Pxx = np.dot( self.P, self.P.T)
        Pxx = Pxx * ( Pxx > cutoffx )
        Pyy = np.dot( self.P.T, self.P )
        Pyy = Pyy * ( Pyy > cutoffy )
        P_nd = self._nd()
        Pxx = self._nd( Pxx )
        Pyy = self._nd( Pyy )

        fig, ax = plt.subplots( figsize = ( 25, 5 ), nrows = 1, ncols = 3 )      
        ax[0].set_title( "P$_{\epsilon}$P$^{T}_{\epsilon}$,  $\epsilon$  : "+str(epsilon)  )
        ax[0].imshow( Pxx );
        ax[1].set_title( "P$^{T}_{\epsilon}$P$_{\epsilon}$ ,  $\epsilon$  : "+str(epsilon) )
        ax[1].imshow( Pyy );
        ax[2].set_title( "P$_{\epsilon}$, $\epsilon$: "+str(epsilon) )
        ax[2].imshow( P_nd );
        plt.savefig( "../Images/NewtonSparsity_images/nnd"+str(index)+".png" )
        plt.show()




