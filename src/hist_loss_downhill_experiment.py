import downhill
import numpy as np
import networkx as nx
import pickle

from itertools import product

from lib.hist_loss.HistLoss import HistLoss
from load_data import *
from settings import PATH_TO_DUMPS

import time


def run_downhill(adjacency_matrix, N, dim, l, neg_sampling, batch_size, batch_count, sparse):
    hist_loss = HistLoss(N, l=l, dim=dim, neg_sampling=neg_sampling)
    hist_loss.setup()

    def get_batch():
        batch_indxs = np.random.choice(a=N, size=batch_size).astype('int32')
        if sparse:
            A_batched = adjacency_matrix[batch_indxs].toarray()
        else:
            A_batched = adjacency_matrix[batch_indxs]
        pos_count = np.count_nonzero(A_batched[:, batch_indxs])
        # pos_count = len(A_batched[:, batch_indxs].nonzero()[0])
        neg_count = batch_size * (batch_size - 1) - pos_count
        neg_sampling_indxs = np.random.choice(a=neg_count, size=pos_count*2).astype('int32')

        return batch_indxs, neg_sampling_indxs, A_batched

    downhill.minimize(
        hist_loss.loss,
        train=get_batch,
        inputs=[hist_loss.batch_indxs, hist_loss.neg_sampling_indxs, hist_loss.A_batched],
        params=[hist_loss.b, hist_loss.w],
        monitor_gradients=True,
        learning_rate=0.1,
        train_batches=batch_count
    )
    return hist_loss.w.get_value(), hist_loss.b.get_value()


if __name__ == '__main__':
    print('Reading graph')
    t = time.time()
    dims = [32]
    ls = [0]

    neg_sampling = True
    batch_size = 100
    batch_count = 100

    sparse = False

    graph, name = load_karate()
    nodes = graph.nodes()
    adjacency_matrix = nx.to_scipy_sparse_matrix(graph, nodes, format='csr')
    N = adjacency_matrix.shape[0]
    if not sparse:
        adj_array = adjacency_matrix.toarray()
    print(time.time() - t)

    for dim, l in product(dims, ls):
        if not sparse:
            w, b = run_downhill(
                adj_array, N, dim, l, neg_sampling, batch_size, batch_count, sparse)
            E = np.dot(adj_array, w) + b
        else:
            w, b = run_downhill(
                adjacency_matrix, N, dim, l, neg_sampling, batch_size, batch_count, sparse)
            E = np.dot(adjacency_matrix, w) + b
        E_norm = E / np.linalg.norm(E, axis=1).reshape((E.shape[0], 1))
        if l != 0:
            filename = '{}/models/hist_loss_l{}_{}_d{}.csv' \
                .format(PATH_TO_DUMPS, l, name, dim)
        else:
            filename = '{}/models/hist_loss_{}_d{}.csv' \
                .format(PATH_TO_DUMPS, name, dim)
        print('Saving results to {}'.format(filename))
        with open(filename, 'w') as file:
            file.write('{} {}\n'.format(N, dim))
            for i in range(N):
                file.write(str(i+1) + ' ' + ' '.join([str(x) for x in E_norm[i]]) + '\n')
