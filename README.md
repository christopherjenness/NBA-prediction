# NBA-prediction
![CI](https://travis-ci.org/christopherjenness/NBA-prediction.svg?branch=master) [![Coverage Status](https://coveralls.io/repos/github/christopherjenness/NBA-prediction/badge.svg?branch=master)](https://coveralls.io/github/christopherjenness/NBA-prediction?branch=master)

Predicts scores of NBA games using matrix completion

## The Model
For a given NBA game, if you could accurately predict each team's offensive rating (points per 100 possessions) and the pace of the game (possessions per game), you could estimate the final score of the game.

Predicting a team's offensive rating against another team is tricky.   It depends on how good the offensive team is at scoring and how good the defending team is a defending.  Most importantly though, it depends on the specific matchups between the two teams.  This is reminiscent of recommendation systems where the recommendation depends on the type of user, the type of product, and the affinity between those two.  Furthermore, for a given season only some offensive ratings between teams are available (the teams that have already played).  The strategy in this model is to use matrix completion techniques to estimate unseen offensive ratings.  These will be combined with pace estimations to predict final scores.

## Matrix completion

Here, we look at two methods for matrix completion: Maximum Margin Matrix Factorization (MMMF) and Singular Value Decomposition (SVD).

Hastie, Trevor, Robert Tibshirani, and Martin Wainwright. Statistical learning with sparsity: the lasso and generalizations. CRC Press, 2015.

### Maximum Margin Matrix Factorization (MMMF)

The objective of MMMF is approximate an _m_ x _n_ matrix **Z** by factoring into 

![Imgur](http://i.imgur.com/2tm9j8P.png)

where **A** is an _m_ x _r_ matrix and **B** is an _n_ x _r_ matrix.  Effectively, this puts a rank constraint _r_ on the approximation **M**.

This can be estimated by solving the following

![Imgur](http://i.imgur.com/eB3O1mC.png)

where Omega indicates that only the known values in **Z** should be taken into consideration.  Any unknown value is treated as zero.

While intuitive, this approach has a two of problems.  First, this is a two dimensional family of models indexed by _r_ (the rank of the factorization) and _lambda_ (the magnitude of regularization), which requires a lot of tuning.  Second, this optomization problem is non-convex and in practice did not find global minima when used to predict NBA offensive ratings.  Because of this, we turned to SVD.

### Singular Value Decomposition Using Nuclear Norm

[SVD](https://en.wikipedia.org/wiki/Singular_value_decomposition), not explained here, can be used to provide a rank-q approximation of a matrix (**Z**) by constraining the rank of the SVD (**M**).  This amounts to the following optimization

![Imgur](http://i.imgur.com/yseXNp9.png)

If values are missing from **Z** then you can constrain **M** to correctly impute these values, while approximating the unknown values

![Imgur](http://i.imgur.com/lPtwang.png)

Where omega is the set of known values.  However, this problem is NP-hard and also leads to overfitting since the known values are required to be predicted exactly.  Instead, you can simultanously predict unknown values and approximate known values by solving the following optimization

![Imgur](http://i.imgur.com/MNwBKvU.png)

Like MMMF, this problem is non-convex.  However, it can be relaxed to the following convex optimization problem 

![Imgur](http://i.imgur.com/lSu054f.png)

where a nuclear norm on **M**, ||**M**||<sub>*</sub> is used. This algorithm, called soft-impute, is studied extensively in:

Mazumder, Rahul, Trevor Hastie, and Robert Tibshirani. "Spectral regularization algorithms for learning large incomplete matrices." Journal of machine learning research 11.Aug (2010): 2287-2322.

##  Example Code

To make predictions, use the following code:

```python
>> model = NBAModel(update=True)
>> model.get_scores('PHO', 'WAS')
PHO WAS
92.9092883132 97.1806398788
```

which predicts the Suns will lose to the Wizards 93-97.  

Note, scraping all the data required to run the algorithm is slow.  This only needs to be done the first time.  On subsequent models, you can use ```update=False``` to used the cached data.

## Model Tuning and Test Error

The optimization strategy above is parameterized by lambda, the extent of regularization.  Using a validation set (10% of sample), we determined 25 to be optimal value of lambda.

![Imgur](http://i.imgur.com/bT7XUCJ.png)

Using lambda = 25 on a held out test set, our model estimates a team's final score with an MSE of 6.7.  Not bad.
