# coding: utf-8

"""Compute the Mahalanobis Distance between each row of x and the data
x    : vector or matrix of data with, say, p columns.
data : ndarray of the distribution from which Mahalanobis distance of each observation of x is to be computed.
cov  : covariance matrix (p x p) of the distribution. If None, will be computed from data.
"""

import scipy as sp
import numpy as np
import scipy.linalg as la

def calc_mahalanobis_distance(x = None, data = None, cov = None):
    x_minus_mu = x - np.mean(data)
    if not cov:
        cov = np.cov(data.values.T)
    inv_covmat = la.inv(cov)
    left_term = np.dot(x_minus_mu, inv_covmat)
    mahal = np.dot(left_term, x_minus_mu.T)
    return mahal.diagonal()

def removing_outlier_with_mahalanobis_distance(df =  None):
    df_return = df.loc[df['mahala'] <= (df['mahala'].mean() + df['mahala'].std() + df['mahala'].describe().iloc[4])]
    return df_return
