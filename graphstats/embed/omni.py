# omni.py
# Created by Jaewon Chung on 2018-09-10.
# Email: j1c@jhu.edu
# Copyright (c) 2018. All rights reserved.

import numpy as np
from sklearn.utils.validation import check_is_fitted

from .embed import BaseEmbed
from ..utils import import_graph


def _check_valid_graphs(graphs):
    """
    Checks if all graphs in list have same shapes.

    Raises an ValueError if there are more than one shape in the input list,
    or if the list is empty.

    Parameters
    ----------
    graphs : list
        List of array-like, (n_vertices, n_vertices).

    Raises
    ------
    ValueError
        If all graphs do not have same shape, or input list is empty.
    """
    shapes = set(map(np.shape, graphs))

    if len(shapes) > 1:
        msg = "There are {} different sizes of graphs.".format(len(shapes))
        raise ValueError(msg)
    elif len(shapes) == 0:
        msg = "No input graphs found."
        raise ValueError(msg)


def _get_omni_matrix(graphs):
    """
    Helper function for creating the omnibus matrix.

    Parameters
    ----------
    graphs : list of graphs
        List of array-like, (n_vertices, n_vertices), or list of 
        networkx.Graph.

    Returns
    -------
    out : 2d-array
        Array of shape (n_vertices * n_graphs, n_vertices * n_graphs)
    """
    n = len(graphs)

    out = (np.tile(np.hstack(graphs),
                   (n, 1)) + np.tile(np.vstack(graphs), (1, n))) / 2

    return out


class OmnibusEmbed(BaseEmbed):
    """
    Omnibus embedding of arbitrary number of input graphs with matched vertex 
    sets.

    Given :math:`A_1, A_2, ..., A_m` a collection of (possibly weighted) adjacency 
    matrices of a collection :math:`m` undirected graphs with matched vertices. 
    Then the :math:`(mn \times mn)` omnibus matrix has the subgraph where 
    :math:`M_{ij} = \frac{1}{2}(A_i + A_j)`. The omnibus matrix is then embedded
    using adjacency spectral embedding.


    Parameters
    ----------
    method: object (default selectSVD)
        the method to use for dimensionality reduction.
    args: list, optional (default None)
        options taken by the desired embedding method as arguments.
    kwargs: dict, optional (default None)
        options taken by the desired embedding method as key-worded
        arguments.

    See Also
    --------
    graphstats.embed.svd.SelectSVD, graphstats.embed.svd.selectDim
    """

    def __init__(self, method=selectSVD, *args, **kwargs):
        super().__init__(method=selectSVD, *args, **kwargs)

    def fit(self, graphs):
        """
		Fit the model with graphs.

		Parameters
		----------
        graphs : list of graphs
            List of array-like, (n_vertices, n_vertices), or list of 
            networkx.Graph.

		Returns
		-------
        lpm : LatentPosition object
            Contains X (the estimated latent positions), Y (same as X if input is
            undirected graph, or right estimated positions if directed graph), and d.
		"""
        # Convert input to np.arrays
        graphs = list(map(import_graph, graphs))

        # Check if the input is valid
        _check_valid_graphs(graphs)

        # Create omni matrix
        omni_matrix = _get_omni_matrix(graphs)

        # Embed
        _reduce_dim(omni_matrix)

        return self.lpm

    def fit_transform(self, graphs):
        """
        Fit the model with graphs and apply the embedding on graphs. 

        n_dimension is either automatically determined or based on user input.

        Parameters
        ----------
        graphs : list of graphs
            List of array-like, (n_vertices, n_vertices), or list of 
            networkx.Graph.

        Returns
        -------
        out : array-like, shape (n_vertices * n_graphs, n_dimension)
        """
        if check_is_fitted(self, ['lpm'], all_or_any=all):
            out = np.dot(self.lpm.X, self.lpm.d)
        else:
            self.fit(graphs)
            out = np.dot(self.lpm.X, self.lpm.d)

        return out
