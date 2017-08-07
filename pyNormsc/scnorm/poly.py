# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 13:48:09 2017

@author: mq44741340
"""

import numpy as np

def poly(x, degree):
    '''
    x: ndarray
    degree: scalar
    '''
    ## check feasibility
    if len(set(x)) < degree:
        print('Insufficient unique data points for specified degree!')
        return None
    centre = np.mean(x)
    x = x - centre
    Q, R = np.linalg.qr(np.polynomial.polynomial.polyvander(x, degree))
    h, tau = np.linalg.qr(np.polynomial.polynomial.polyvander(x, degree), 'raw')
    ## rescaling of Q by h.T
    X = (Q * np.diag(h.T))[:, 1:]
    X2 = X ** 2
    norm2 = X2.sum(0)
    alpha = np.dot(X2.T, x) / norm2
    beta = norm2 / (np.append([len(x)], norm2[:-1]))
    scale = np.sqrt(norm2)
    X = X * (1 / scale)
    return X, centre, scale, alpha[:-1], beta[:-1]

def predict_poly(X, centre, scale, alpha, beta, x):
    '''
        X, centre, scale, alpha, beta: returns from poly function
        x: new data to be predicted
    '''
    degree = X.shape[1]
    x = x - centre
    X = np.array(x.tolist() * degree).reshape((len(x), degree), order='F')
    if degree > 1:
        ## second polynomial
        X[:, 1] = (x - alpha[0]) * X[:, 0] - beta[0]
        ## further polynomials obtained from recursion
        i = 2
        while i < degree:
            X[:, i] = (x - alpha[i-1]) * X[:, i-1] - beta[i-1] * X[:, i-2]
            i += 1
        return X * (1 / scale)
    else:
        return None