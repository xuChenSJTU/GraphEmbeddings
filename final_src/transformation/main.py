from itertools import product
from pathlib import Path

from transformation.HistLossConfiguration import HistLossConfiguration
from transformation.RunConfiguration import RunConfiguration
from transformation.Runner import run

if __name__ == '__main__':

    methods = ['deepwalk', 'node2vec']

    metrics = ['EMD']
    simmatrix_methods = ['ID', 'ADA']
    loss_methods = ['ASIM']
    calc_pos_methods = ['NORMAL', 'WEIGHTED']
    calc_neg_methods = ['NORMAL', 'WEIGHTED', 'IGNORE_NEG']
    calc_hist_methods = ['TF-KDE']
    batch_sizes = [0]

    for (metric,
         simmatrix_method,
         loss_method,
         calc_pos_method,
         calc_neg_method,
         calc_hist_method,
         batch_size) in product(metrics,
                                simmatrix_methods,
                                loss_methods,
                                calc_pos_methods,
                                calc_neg_methods,
                                calc_hist_methods,
                                batch_sizes):
        if calc_neg_method != calc_pos_method:
            continue
        methods += ['hist_loss_' +
                    str(HistLossConfiguration(metric,
                                              simmatrix_method,
                                              loss_method,
                                              calc_pos_method,
                                              calc_neg_method,
                                              calc_hist_method,
                                              batch_size))]

    dimensions = [4, 8, 16, 32]
    names = ['football', 'karate', 'stars', 'polbooks', 'email']

    for (method, name, dim) in product(methods, names, dimensions):
        print(method, name, dim)
        try:
            run(RunConfiguration(method, name, dim), path_to_dumps=Path('./dumps').absolute())
        except Exception as e:
            print(e)
