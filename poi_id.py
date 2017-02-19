#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data, test_classifier

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV # for sklearn 0.18
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import precision_recall_curve, precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.feature_selection import SelectKBest, f_classif, chi2

#%% F E A T U R E     S E L E C T I O N

features_list = ['poi','salary', 'deferral_payments', 'total_payments', 'loan_advances', 'bonus', 'restricted_stock_deferred', 'deferred_income', 'total_stock_value', 'expenses', 'exercised_stock_options', 'other', 'long_term_incentive', 'restricted_stock', 'director_fees', 'to_messages', 'from_poi_to_this_person', 'from_messages', 'from_this_person_to_poi', 'shared_receipt_with_poi'] 
#features_list = ['poi', 'total_payments', 'total_stock_value'] 

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)


data = featureFormat(data_dict, features_list, sort_keys = True)
df = pd.DataFrame(data, columns=features_list)

### Create scatter matrix to first check for outliers    
#sns.plt.figure(1, figsize=(10,10))

#g=sns.PairGrid(df,hue="poi")
#g.map_lower(plt.scatter)
#g.map_diag(plt.hist)
#g.map_upper(sns.boxplot)
#sns.plt.show()


#sns.plt.figure(2, figsize=(10,5))
#for fe in features_list:
#    sns.boxplot(df[fe])
#    sns.plt.show()


# Output outliers
#for i in data_dict:
#    if data_dict[i]['loan_advances'] == df.loan_advances.max():
#        print i, ': ', data_dict[i]['loan_advances'], data_dict[i]['poi']

#for i in data_dict:
#    if data_dict[i]['restricted_stock_deferred' ] == df.restricted_stock_deferred.max():
#        print i, ': ', data_dict[i]['restricted_stock_deferred'], data_dict[i]['poi']
#        print data_dict[i]
        
#for i in data_dict:
#    if data_dict[i]['restricted_stock' ] == df.restricted_stock.min():
#        print i, ': ', data_dict[i]['restricted_stock'], data_dict[i]['poi']
#        print data_dict[i]        

# Remove outliers    
data_dict.pop('TOTAL', 0)
data_dict.pop('BHATNAGAR SANJAY', 0)
data_dict.pop('BELFER ROBERT', 0)


#%% Remove total_payments and total_stock_value from featureList
features_list = ['poi','salary', 'deferral_payments', 'loan_advances', 'bonus', 'restricted_stock_deferred', 'deferred_income', 'expenses', 'exercised_stock_options', 'other', 'long_term_incentive', 'restricted_stock', 'director_fees', 'to_messages', 'from_poi_to_this_person', 'from_messages', 'from_this_person_to_poi', 'shared_receipt_with_poi'] 

data = featureFormat(data_dict, features_list, sort_keys = True)    



### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
my_dataset = data_dict


#%%
### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

random_state = 42

features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.2, random_state=random_state)

#%% Classifier Comparison: Step1: Classifiers with default parameters



classifiers = [
        GaussianNB(),
        KNeighborsClassifier(),
        DecisionTreeClassifier(random_state=random_state),
        RandomForestClassifier(random_state=random_state),
        SVC(random_state=random_state)]

names = ['GaussianNB', 'KNearestNeighbors', 'Decision Tree', 'Random Forest', 'Support Vector Classifier']

color = ['#4286f4', '#207f1e', '#7c2915', '#cc8006', '#b50e0e']

precision = []
recall = []
f1 = []

#%% Step 1

for i, clf in enumerate(classifiers):
    print 'Step 1: ', i, names[i]
    
    clf.fit(features_train, labels_train)
       
    pred = clf.predict(features_test)
        
    print "Precision: ", precision_score(labels_test, pred)
    print "Recall:    ", recall_score(labels_test, pred)
    print "F1:        ", f1_score(labels_test, pred)

    precision.append(precision_score(labels_test, pred))
    recall.append(recall_score(labels_test, pred))
    f1.append(f1_score(labels_test, pred))
   
    print 'done...'
    
print '-------------------------------------------------------------------------------'    


#%% Step 2: 

classifier_opt = []    
    
parameters = [
        dict(),
        dict(n_neighbors= range(1,20,1),
             weights=['uniform', 'distance']),
        dict(criterion = ['gini', 'entropy'], 
             min_samples_split = [2, 4, 10, 20],
             min_samples_leaf = range(1,11,1)),
        dict(criterion = ['gini', 'entropy'], 
             n_estimators = [5, 8, 10, 12, 25],
             #min_samples_leaf = range(1,11,1),
             min_samples_split = [2, 4, 10, 20]),
        dict(C = [1, 5, 10, 100], 
             gamma = [1, 10, 100, 1000])
        ]    
    
    
for i, classifier in enumerate(classifiers):
    print 'Step 2: ', i, names[i]
    
    # Min Max Scaler except for decision tree and random forest
    if (i==0) | (i==1) | (i==4):
        features_train = MinMaxScaler().fit_transform(features_train)
        features_test = MinMaxScaler().fit_transform(features_test)
    
    
    sss = StratifiedShuffleSplit(n_splits=30, test_size=0.2, random_state=random_state)
    clf = GridSearchCV(classifier, parameters[i], cv=sss, scoring='f1')
    
    clf.fit(features_train, labels_train)
    
    clf = clf.best_estimator_
    
    print clf
    
    pred = clf.predict(features_test)
        
    print "Precision: ", precision_score(labels_test, pred)
    print "Recall:    ", recall_score(labels_test, pred)
    print "F1:        ", f1_score(labels_test, pred)

    precision.append(precision_score(labels_test, pred))
    recall.append(recall_score(labels_test, pred))
    f1.append(f1_score(labels_test, pred))
    
    classifier_opt.append(clf)
    
   
    print 'done...'
    
print '-------------------------------------------------------------------------------'    

#%%

    
#%% Step 3

print "Step 4: Decision Tree Optimization"



classifier = DecisionTreeClassifier()

parameters = dict(CLF__criterion = ['gini', 'entropy'], 
             CLF__min_samples_split = [2, 4, 10, 20], 
             CLF__min_samples_leaf = range(1,11,1),
             features__pca__n_components=range(1, len(features_list)-1),
             features__select__k=range(1,8))

combined_features = FeatureUnion([('pca', PCA()), ('select', SelectKBest())])

estim = [('features', combined_features), ('CLF', classifier)]

pipe = Pipeline(estim) 
    
#sss = StratifiedShuffleSplit(n_splits=100, test_size=.3, random_state=random_state)
sss = StratifiedShuffleSplit(n_splits=30, test_size=.2, random_state=random_state)
    
clf = GridSearchCV(pipe, parameters, scoring='f1', cv=sss)
    
clf.fit(features_train, labels_train)
    
clf = clf.best_estimator_

pred = clf.predict(features_test)
        
print "Precision: ", precision_score(labels_test, pred)
print "Recall:    ", recall_score(labels_test, pred)
print "F1:        ", f1_score(labels_test, pred)
    
#%%


dump_classifier_and_data(clf, my_dataset, features_list)

