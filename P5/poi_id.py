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

#%% Dataset Description

features_list = ['poi','salary', 'deferral_payments', 'total_payments', 'loan_advances', 'bonus', 'restricted_stock_deferred', 'deferred_income', 'total_stock_value', 'expenses', 'exercised_stock_options', 'other', 'long_term_incentive', 'restricted_stock', 'director_fees', 'to_messages', 'from_poi_to_this_person', 'from_messages', 'from_this_person_to_poi', 'shared_receipt_with_poi'] 

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

number_poi = 0
for i in data_dict:
    if data_dict[i]['poi']:
        number_poi +=1

print "Total number of entries: ", len(data_dict)
print "Total number of POIs:    ", number_poi
print "Number of features:      ", len(data_dict['ALLEN PHILLIP K'])

#%% Outlier removal

data = featureFormat(data_dict, features_list, sort_keys = True)
df = pd.DataFrame(data, columns=features_list)

feature_retained = []

for fe in features_list:
    
    iZero = df[fe] == 0
    percentageZero = float(sum(iZero))/float(len(iZero)) * 100          
    print "NaNs: ", percentageZero, '%'
    
    # check if more than 75% of the feature is missing. If not retain the feature for further analysis
    if (percentageZero <= 75) | (fe=='poi'):
        feature_retained.append(fe)
    sns.plt.figure(figsize=(20,10))                         
    sns.boxplot(df[fe])
    sns.plt.show()


# Output outliers
for i in data_dict:
    if data_dict[i]['loan_advances'] == df.loan_advances.max():
        print i, ': ', data_dict[i]['loan_advances'], data_dict[i]['poi']

for i in data_dict:
    if data_dict[i]['restricted_stock_deferred' ] == df.restricted_stock_deferred.max():
        print i, ': ', data_dict[i]['restricted_stock_deferred'], data_dict[i]['poi']
        print data_dict[i]
        
for i in data_dict:
    if data_dict[i]['restricted_stock' ] == df.restricted_stock.min():
        print i, ': ', data_dict[i]['restricted_stock'], data_dict[i]['poi']
        print data_dict[i]        

#%%

# Remove outliers    
data_dict.pop('TOTAL', 0)
data_dict.pop('BHATNAGAR SANJAY', 0)
data_dict.pop('THE TRAVEL AGENCY IN THE PARK', 0)

data = featureFormat(data_dict, features_list, sort_keys = True)
df = pd.DataFrame(data, columns=features_list)

for i in data_dict:
    if data_dict[i]['loan_advances'] == df.loan_advances.max():
        print i, ': ', data_dict[i]['loan_advances'], data_dict[i]['poi']

for i in data_dict:
    if data_dict[i]['restricted_stock_deferred' ] == df.restricted_stock_deferred.max():
        print i, ': ', data_dict[i]['restricted_stock_deferred'], data_dict[i]['poi']
        print data_dict[i]
        
for i in data_dict:
    if data_dict[i]['restricted_stock' ] == df.restricted_stock.min():
        print i, ': ', data_dict[i]['restricted_stock'], data_dict[i]['poi']
        print data_dict[i] 


data_dict.pop('BELFER ROBERT', 0)

# Remove total_payments and total_stock_value from list
for i, fe in enumerate(feature_retained):
    if (fe == 'total_payments') | (fe == 'total_stock_value'):
        feature_retained.pop(i)

#%% Create new features

for i in data_dict:
    
    if (data_dict[i]['from_this_person_to_poi'] != 'NaN') | (data_dict[i]['from_messages'] != 'NaN'):    
        data_dict[i]['frac_from_poi'] = float(data_dict[i]['from_this_person_to_poi']) / float(data_dict[i]['from_messages'])
    else:
        data_dict[i]['frac_from_poi'] = 'NaN'
        
    if (data_dict[i]['from_poi_to_this_person'] != 'NaN') | (data_dict[i]['to_messages'] != 'NaN'):    
        data_dict[i]['frac_to_poi'] = float(data_dict[i]['from_poi_to_this_person']) / float(data_dict[i]['to_messages'])
    else:
        data_dict[i]['frac_to_poi'] = 'NaN'

#%%
feature_retained.append('frac_from_poi')
feature_retained.append('frac_to_poi')

features_list = feature_retained

# Store to my_dataset for easy export below.
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


#%% Step 1

for i, clf in enumerate(classifiers):
    print 'Step 1: ', i, names[i]
    
    clf.fit(features_train, labels_train)
       
    pred = clf.predict(features_test)
        
    print "Precision: ", precision_score(labels_test, pred)
    print "Recall:    ", recall_score(labels_test, pred)
    print "F1:        ", f1_score(labels_test, pred)

    print 'done...'

for clf in classifiers:
    test_classifier(clf, my_dataset, features_list)
    
print '-------------------------------------------------------------------------------'    


#%% Step 2: 

classifier_opt = []    
    
parameters = [
        dict(),
        dict(n_neighbors= range(1,20,1),
             weights=['uniform', 'distance']),
        dict(criterion = ['gini', 'entropy'], 
             min_samples_split = range(10, 30, 1),
             min_samples_leaf = range(1,11,1)),
        dict(criterion = ['gini', 'entropy'], 
             n_estimators = [5, 8, 10, 12, 25],
             min_samples_split = [2, 4, 10, 20]),
        dict(kernel = ['rbf', 'linear', 'poly', 'sigmoid'],
             C = [1, 10, 100],
             gamma = [1, 10, 1000])
        ]    
    
    
for i, classifier in enumerate(classifiers):
    print 'Step 2: ', i, names[i]
    
    # Min Max Scaler except for decision tree and random forest
    if (i==0) | (i==1) | (i==4):
        Scaler = MinMaxScaler()
        features_train = Scaler.fit_transform(features_train)
        features_test = Scaler.transform(features_test)
    
    
    sss = StratifiedShuffleSplit(n_splits=30, test_size=0.2, random_state=random_state)
    clf = GridSearchCV(classifier, parameters[i], cv=sss, scoring='f1')
    
    clf.fit(features_train, labels_train)
    
    print "Best score: ", clf.best_score_
    
    clf = clf.best_estimator_
    
    print clf
    
    pred = clf.predict(features_test)
        
    print "Precision: ", precision_score(labels_test, pred)
    print "Recall:    ", recall_score(labels_test, pred)
    print "F1:        ", f1_score(labels_test, pred)
    
    classifier_opt.append(clf)
    
    print 'done...'
    print " "

for clf in classifier_opt:
    test_classifier(clf, my_dataset, features_list)
    
print '-------------------------------------------------------------------------------'    



#%% Step 3a

print "Step 3a: Decision Tree Optimization"

classifier = DecisionTreeClassifier(random_state=random_state)

parameters = dict(criterion = ['gini', 'entropy'],
             max_features = range(1,len(features_list),1),
             max_depth = range(1, 5, 1),
             min_samples_split = [2,3, 4],
             min_samples_leaf = [2, 3, 4, 5],
             max_leaf_nodes = [10, 11],
             splitter = ['random'],
             class_weight = ['balanced'],
             presort = [False, True])

  
sss = StratifiedShuffleSplit(n_splits=60, test_size=.2, random_state=random_state)
    
clf = GridSearchCV(classifier, parameters, scoring='f1', cv=sss)
    
clf.fit(features_train, labels_train)

print "Best score: ", clf.best_score_    
clf = clf.best_estimator_

pred = clf.predict(features_test)
        
print "Precision: ", precision_score(labels_test, pred)
print "Recall:    ", recall_score(labels_test, pred)
print "F1:        ", f1_score(labels_test, pred)

test_classifier(clf, my_dataset, features_list)

print "Feature Importance: "
for i, j in enumerate(clf.feature_importances_):
    print("%(fe)25s : %(nu)5.5f" % {'fe': features_list[i+1], 'nu': j})#, j
 
#%% Step 3b Feature selection

print "Step 3b: Decision Tree Optimization"

features_list_new = ['poi']

for i, j in enumerate(clf.feature_importances_):
    if j > 0:
        features_list_new.append(features_list[i+1])

print features_list_new

data = featureFormat(my_dataset, features_list_new, sort_keys = True)
labels, features = targetFeatureSplit(data)

features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.2, random_state=random_state)

parameters = dict(criterion = ['gini', 'entropy'],
             max_features = range(1,len(features_list_new),1),
             max_depth = range(1, 5, 1),
             min_samples_split = [2,3, 4],
             min_samples_leaf = [2, 3, 4, 5],
             max_leaf_nodes = [10, 11],
             splitter = ['random'],
             class_weight = ['balanced'],
             presort = [False, True])

sss = StratifiedShuffleSplit(n_splits=60, test_size=.2, random_state=random_state)
    
clf = GridSearchCV(classifier, parameters, scoring='f1', cv=sss)

clf.fit(features_train, labels_train)

print "Best score: ", clf.best_score_    
clf = clf.best_estimator_

pred = clf.predict(features_test)
        
print "Precision: ", precision_score(labels_test, pred)
print "Recall:    ", recall_score(labels_test, pred)
print "F1:        ", f1_score(labels_test, pred)



test_classifier(clf, my_dataset, features_list_new)

#%% Step 4: Final classifier

# Compare performance without newly created features: max_features is adapted to removal of new features!!
clf = DecisionTreeClassifier(class_weight='balanced', criterion='entropy', 
                             max_depth=1, max_features=14, max_leaf_nodes=10,min_samples_leaf=2, 
                             min_samples_split=2, presort=False, random_state=42, splitter='random')

# remove frac_from_poi and frac_to_poi
features_list_reduced = ['poi',
 'salary',
 'deferral_payments',
 'bonus',
 'deferred_income',
 'expenses',
 'exercised_stock_options',
 'other',
 'long_term_incentive',
 'restricted_stock',
 'to_messages',
 'from_poi_to_this_person',
 'from_messages',
 'from_this_person_to_poi',
 'shared_receipt_with_poi']

data = featureFormat(my_dataset, features_list_reduced, sort_keys = True)
labels, features = targetFeatureSplit(data)

features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.2, random_state=random_state)

clf.fit(features_train, labels_train)

pred = clf.predict(features_test)
        
print "Precision: ", precision_score(labels_test, pred)
print "Recall:    ", recall_score(labels_test, pred)
print "F1:        ", f1_score(labels_test, pred)

test_classifier(clf, my_dataset, features_list_reduced)

# Final classifier
clf = DecisionTreeClassifier(class_weight='balanced', criterion='entropy', 
                             max_depth=1, max_features=15, max_leaf_nodes=10,min_samples_leaf=2, 
                             min_samples_split=2, presort=False, random_state=42, splitter='random')

data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.2, random_state=random_state)

clf.fit(features_train, labels_train)

pred = clf.predict(features_test)
        
print "Precision: ", precision_score(labels_test, pred)
print "Recall:    ", recall_score(labels_test, pred)
print "F1:        ", f1_score(labels_test, pred)

test_classifier(clf, my_dataset, features_list)

dump_classifier_and_data(clf, my_dataset, features_list)

