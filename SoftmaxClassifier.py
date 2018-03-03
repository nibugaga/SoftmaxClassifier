# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 18:20:39 2018

@author: Arthur
"""
import numpy as np
import time
from sklearn.base import BaseEstimator

class SoftmaxClassifier(BaseEstimator):
    
    def __init__(self, n_iters=5000, eta=0.01, alpha=0, verbose=0, early_stopping = False):
        '''
        n_iters : # iterations
        eta : learning rate
        alpha : l2 regularization paramater
        verbose : 0 not info printing / 1 last result for cost function / 2 printing cost function 10 times
        '''
        self.n_iters = n_iters
        self.eta = eta
        self.alpha = alpha
        self.verbose = verbose
        self.early_stopping = early_stopping
    
    def fit(self, X, y):
        '''
        Input : - X     : (m , n+1)
                - y     : (m, K)
        '''
        ti = time.time()
        t = 0
        X_b = self.add_bias(X)
        y = y.astype(int)
        y_one_hot = self.to_one_hot(y)
        
        m, n = X.shape
        K = y.shape[1]
        
        
        # random initialize theta
        try:
            theta = self.theta
            if np.isnan(self.softmax_cost_func(theta, X_b, y_one_hot, self.alpha)):
                theta = np.random.randn(n+1, K)
            print('b')
        except:
            theta = np.random.randn(n+1, K)
            print('a')
            while np.isnan(self.softmax_cost_func(theta, X_b, y_one_hot, self.alpha)):
                theta = np.random.randn(n+1, K)
        
        self.theta = theta
        best_J = self.softmax_cost_func(theta, X_b, y_one_hot, self.alpha)
        
        for i in range(self.n_iters):
            
            grad = self.batch_grad_descent_softmax(theta, X_b, y_one_hot, self.alpha)
            theta = theta - self.eta*grad
            
            if self.verbose == 2 and i%(self.n_iters/10) == 0:
                print('iter ', i, '\t', ' J : ', self.softmax_cost_func(theta, X_b, y_one_hot, self.alpha))
            
            J = self.softmax_cost_func(theta, X_b, y_one_hot, self.alpha)
            
            
            if self.early_stopping:
                if i==10:
                    best_J = J
                if i>10:
                    if J < best_J:
                        best_J = J
                        self.theta = theta
                        t = i
                    else:
                        if i - t > 20:
                            print('\n')
                            print('Early stopping @ iter ', i+1, '\t', 'Best J :', best_J)
                            break
        
        if self.verbose == 1 or self.verbose == 2 and not self.early_stopping:
            print('iter ', self.n_iters, '\t', ' J : ', self.softmax_cost_func(theta, X_b, y_one_hot, self.alpha))
        
        if self.verbose == 1 or self.verbose == 2:
            tf = time.time()
            print('\n')
            print('time of execution :', tf-ti, 's')
        
        return self
    
    def predict(self, X):
        '''
        input : X (m, n)
        output : y (m, 1)
        '''
        X_b = self.add_bias(X)
        
        z = X_b.dot(self.theta)
        P = self.softmax_func(z)
        best_k = np.argmax(P, axis = 1).reshape(-1,1)
        
        return best_k
        

    def add_bias(self, X):
        
        m, n = X.shape
        
        return np.c_[np.ones((m,1)), X]
        
    def to_one_hot(self, y):
        '''
        One hot a column of label y to K column, one for each classes
        '''
        K = len(np.unique(y))
        m = y.shape[0]
        
        y_one_hot = np.zeros((m, K))

        y_one_hot[np.arange(m), y.ravel()] = 1
        
        return y_one_hot

    def softmax_func(self, z):
        '''
        Return the softmax function of z (a probability tensor)
        '''
        exp_z = np.exp(z)
        N = np.sum(exp_z, axis=1, keepdims=True)
        p = exp_z / N

        return p
        
        
    def softmax_cost_func(self, theta, X, y, alpha):
        '''
        Input : - theta : (n+1 , K)
                - X     : (m , n+1)
                - y     : (m, K)
        Output : J : cross entropy cost function (scalar)
        '''
        m = X.shape[0]
        z = X.dot(theta)

        epsilon = 1e-7
        
        l2_reg = (self.alpha/2) * np.trace(theta.T.dot(theta))
        
        J = -(1/m) *  np.trace(y.T.dot(np.log(self.softmax_func(z) + epsilon))) + l2_reg
        return J
    
    def batch_grad_descent_softmax(self, theta, X, y, alpha):
        '''
        Input : - theta : (n+1 , K)
                - X     : (m , n+1)
                - y     : (m, K)
        Output : grad (n+1, K) : gradient of the cross entropy cost function relative to theta
        '''
        
        m = X.shape[0]
        K = theta.shape[1]
        z = X.dot(theta)
        
        l2_reg = self.alpha * np.r_[np.zeros((1,K)), theta[1:]]
        
        grad = (1/m) * X.T.dot(self.softmax_func(z) - y) + l2_reg
        
        return grad


#X = np.load('datasets/MNIST/mnist_data.npy')
#y = np.load('datasets/MNIST/mnist_label.npy').reshape(-1,1)
#
#from sklearn.preprocessing import StandardScaler
#
#X = StandardScaler().fit_transform(X)
#
#from sklearn.model_selection import train_test_split
#
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
#
#softmax_clf = SoftmaxClassifier(n_iters=100, eta=0.001, alpha=0.01, verbose=2)
#
#softmax_clf.fit(X_train, y_train)






#def train_test_custom_split(X, y, frac_test=0.2):
#    '''
#    Split X and y to a train and test set
#    output : X_train, X_test, y_train, y_test
#    '''
#    m = X.shape[0]
#    
#    rand_idx = np.random.permutation(m)
#    limit = int(frac_test*(1-m))
#    
#    X_perm = X[rand_idx, :]
#    y_perm = y[rand_idx, :]
#    
#    X_train, y_train = X_perm[0:limit] , y_perm[0:limit]
#    X_test, y_test = X_perm[limit:] , y_perm[limit:]
#    
#    return X_train, X_test, y_train, y_test     




#from sklearn import datasets
#
#iris = datasets.load_iris()
#
#X = iris['data'] # petal length, petal width
#y = iris['target'].reshape(-1,1)
#
#m, n = X.shape
#K = len(np.unique(y))
#
#X_train, X_test, y_train, y_test = train_test_custom_split(X, y, frac_test=0.4)
#
#softmax_clf = SoftmaxClassifier(n_iters=100000, verbose=2, eta=0.001, alpha=0.1, early_stopping=True)
#
#softmax_clf.fit(X_train, y_train)
#
#y_test_pred = softmax_clf.predict(X_test)
#accuracy = (y_test_pred == y_test).mean()
#print('accuracy : ', accuracy)
#
#from sklearn.pipeline import Pipeline
#from sklearn.preprocessing import StandardScaler
#
#pipe_softmax = Pipeline([
#        ('StandardScaler', StandardScaler()),
#        ('softmax_clf', SoftmaxClassifier(n_iters=100000, verbose=2, eta=0.001, alpha=0.1, early_stopping=True))
#        ])
#    
#pipe_softmax.fit(X_test, y_test)
#y_test_pred = pipe_softmax.predict(X_test)
#accuracy = (y_test_pred == y_test).mean()
#print('accuracy : ', accuracy)