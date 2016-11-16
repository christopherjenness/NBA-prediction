import numpy
import pandas as pd

def matrix_factorization(R, P, Q, K, steps=20000, alpha=0.0002, beta=0.02):
    """
    Stolen from:
    http://www.quuxlabs.com/blog/2010/09/matrix-factorization-a-simple-tutorial-and-implementation-in-python/
    """
    Q = Q.T
    for step in xrange(steps):
        print step
        for i in xrange(len(R)):
            for j in xrange(len(R[i])):
                if R[i][j] > 0:
                    eij = R[i][j] - numpy.dot(P[i,:],Q[:,j])
                    for k in xrange(K):
                        P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
        eR = numpy.dot(P,Q)
        e = 0
        for i in xrange(len(R)):
            for j in xrange(len(R[i])):
                if R[i][j] > 0:
                    e = e + pow(R[i][j] - numpy.dot(P[i,:],Q[:,j]), 2)
                    for k in xrange(K):
                        e = e + (beta/2) * ( pow(P[i][k],2) + pow(Q[k][j],2) )
        if e < 0.001:
            break
    return P, Q.T

R_pace = numpy.genfromtxt('pace.csv', delimiter=',', skip_header=1)[:, 1:]
R_OR = numpy.genfromtxt('OR.csv', delimiter=',', skip_header=1)[:, 1:]


N = 30
M = 30
K = 5

P = numpy.random.rand(N,K)
Q = numpy.random.rand(M,K)

nP, nQ = matrix_factorization(R_pace, P, Q, 5)
nR_pace = numpy.dot(nP, nQ.T)
nP, nQ = matrix_factorization(R_OR, P, Q, 5)
nR_OR = numpy.dot(nP, nQ.T)

predictions = nR_pace * nR_OR / 100 

predictions = pd.DataFrame(predictions, index=teams, columns=teams )
predictions.to_csv('predictions.csv')



def get_scores(team1, team2, predictions=predictions):
    team1s = predictions.loc[team1][team2]
    team2s = predictions.loc[team2][team1]
    print team1, team2
    print team1s, team2s
    print ''
    
get_scores('CHO', 'CLE')
get_scores('ORL', 'OKC')
get_scores('LAL', 'MIN')
get_scores('PHO', 'GSW')
get_scores('DEN', 'POR')


