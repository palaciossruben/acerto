
import xgboost as xgb

from sklearn import datasets

iris = datasets.load_iris()
X = iris.data
y = iris.target
print(X)

from sklearn.cross_validation import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)


#from sklearn.datasets import dump_svmlight_file

#dump_svmlight_file(X_train, y_train, 'dtrain.svm', zero_based=True)
#dump_svmlight_file(X_test, y_test, 'dtest.svm', zero_based=True)
#dtrain_svm = xgb.DMatrix('dtrain.svm')
#dtest_svm = xgb.DMatrix('dtest.svm')

param = {
    'max_depth': 3,  # the maximum depth of each tree
    'eta': 0.3,  # the training step for each iteration
    'silent': 1,  # logging mode - quiet
    'objective': 'multi:softprob',  # error evaluation for multiclass training
    'num_class': 3}  # the number of classes that exist in this datset
num_round = 20  # the number of training iterations

bst = xgb.train(param, dtrain, num_round)

print(bst.predict(dtest))

prediction = list(bst.predict(dtest))
#print([list(triad).index(max(triad)) for triad in prediction])

#print(y_test)

#bst.



# dump in readable form
#bst.dump_model('dump.raw.txt')
