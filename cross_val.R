library('softImpute')
library('caret')
set.seed(123)

# Load and organize pace and offensive rating data
df.pace <- read.csv('pace.csv')
df.OR <- read.csv('OR.csv')

df.pace = df.pace[,seq(2, 31)]
df.OR = df.OR[,seq(2, 31)]

df.pace[df.pace == 0] <- NA
df.OR[df.OR==0] = NA

df.pace = as.matrix(df.pace)
df.OR = as.matrix(df.OR)

played.games = seq(900)[!is.na(df.pace)]

# Computes MSE for a partition of the data (validation or test set)
MSE.calc <- function(k, lambda){
  pace.vector = c(df.pace)
  OR.vector = c(df.OR)
  validation.pace = pace.vector[played.games[folds==k]] 
  validation.OR = OR.vector[played.games[folds==k]] 
  pace.vector[played.games[folds==k]] <- NA
  pace.vector[played.games[folds==1]] <- NA
  df.paceCV = matrix(pace.vector, nrow=30, ncol=30)
  OR.vector[played.games[folds==k]] <- NA
  OR.vector[played.games[folds==1]] <- NA
  df.ORCV = matrix(OR.vector, nrow=30, ncol=30)
  
  fits.pace = softImpute(x=df.paceCV, trace=TRUE, type="svd", lambda=lambda, rank.max = 5)
  pace = fits.pace$u %*% diag(fits.pace$d) %*% t(fits.pace$v)
  fits.OR=softImpute(x=df.OR,trace=TRUE, type="svd", lambda=lambda, rank.max = 5)
  OR = fits.OR$u %*% diag(fits.OR$d) %*% t(fits.OR$v)
  
  predicted.pace = c(pace)
  predictions.pace = predicted.pace[played.games[folds==k]]
  predicted.OR = c(OR)
  predictions.OR = predicted.OR[played.games[folds==k]]
  scores = validation.OR * validation.pace / 100
  predictions = predicted.OR * predicted.pace / 100
  predictions.CV = predictions[played.games[folds==k]] 
  
  MSE = mean(((predictions.CV  - scores) * (predictions.CV  - scores))^0.5)
  return(MSE)
}

# Test validation error on each lambda
folds <- createFolds(played.games, k = 10, list = FALSE, returnTrain = FALSE)
lambdas = seq(9)**2
MSEs= vector()

for(k in seq(9)){
  MSE = MSE.calc(2, lambdas[k])
  MSEs = append(MSEs, MSE)
}

# Plot validation errors
plot(lambdas, MSEs, xlab = 'Lambda', ylab = 'MSE', main='Validation Error')

# Test Error on holdout data 
test.error = MSE.calc(1, 25)
