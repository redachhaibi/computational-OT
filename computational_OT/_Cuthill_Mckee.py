import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import reverse_cuthill_mckee
import matplotlib.pyplot as plt


class _Expcuthill_mckee:
    def __init__( self, P ):
        """

        Parameters:
        -----------
            P : ndarray, shape (n,m)
                The coupling of the probability histograms of size n and m.
                
        """
        self.P = P
        self.P_xx = np.dot( P, P.T )
        self.P_yy = np.dot( P.T, P )

    def _invert_permutation( self, p ):
        """
        
        Parameters:
        -----------
            p : ndarray, shape  (n,m)
                Permutation matrix obtained from the reverse Cuthill Mckee algorithm.
            

        Returns:
        --------
            An array s for which np.array_equal(arr[p][s], arr) is True.
            The array_like argument p must be some permutation of 0, 1, ..., len(p)-1.
        """
        p = np.asanyarray( p ) # in case p is a tuple, etc.
        s = np.empty_like( p )
        s[p] = np.arange( p.size )
        return s

    def _evaluate( self, cut_offx = 0, cut_offy = 0, epsilon = 0, index = 0 ):
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
        P_xx_   = self.P_xx * ( self.P_xx > cut_offx )
        P_xx_csr = csr_matrix( P_xx_ )
        perm_x = reverse_cuthill_mckee( P_xx_csr )
        invp_x = self._invert_permutation( perm_x )

        P_yy_ = self.P_yy * ( self.P_yy > cut_offy )
        P_yy_csr = csr_matrix( P_yy_ )
        perm_y = reverse_cuthill_mckee( P_yy_csr )
        invp_y = self._invert_permutation( perm_y )

        # mesh = np.meshgrid( perm_x, perm_y )
        # P_ = P[mesh]
        # mesh = np.meshgrid( perm_x, perm_x )
        # P_xx_ = P_xx[mesh]
        # mesh = np.meshgrid( perm_y, perm_y )
        # P_yy_ = P_yy[mesh]

        mesh_x, mesh_y = np.meshgrid( perm_x, perm_y )
        P_ = self.P[ mesh_x, mesh_y ]
        mesh_x, mesh_y = np.meshgrid( perm_x, perm_x )
        P_xx_ = self.P_xx[ mesh_x, mesh_y ] 
        mesh_x, mesh_y = np.meshgrid( perm_y, perm_y )
        P_yy_ = self.P_yy[ mesh_x, mesh_y ]

    
        fig, ax = plt.subplots( figsize = ( 25, 5 ), nrows = 1, ncols = 3 )
        ax[0].set_title( "P$_{\epsilon}$P$^{T}_{\epsilon}$ , cutoff: " + str(cut_offx) + " and $\epsilon$ : "+str(epsilon)  )
        ax[0].imshow( P_xx_ );
        ax[1].set_title( "P$^{T}_{\epsilon}$P$_{\epsilon}$ , cutoff: " + str(cut_offy) +  " and $\epsilon$ : "+str(epsilon) )
        ax[1].imshow( P_yy_ );
        ax[2].set_title( "P$_{\epsilon}$  and $\epsilon$ : "+str(epsilon) )
        ax[2].imshow( P_ );
        # ax[3].set_title("P_xx  and e : "+str(epsilon)  )
        # ax[3].imshow( self.P_xx );
        plt.savefig( "../Images/NewtonSparsity_images/RCM"+str(index)+".png" )
        plt.show()
