# FeatureCloud Cross-Validation app
The Cross Validation app in FeatureCloud library creates local splits for a k-fold cross validation. It can be used as one of the
first apps in FC workflow and can be followed by different Machine Learning or Data analysis apps.

## Input
Similar to Data Distributor app, Cross-Validation (CV) accepts Numpy files (`.npy`, `.npz`) files alongside `.csv` and `.txt` files.
For `.csv` and `.txt` files, clients should identify the delimiter character using `sep` key in the config file. For numpy file 
they have to choose from three possible options for `target_value`:
- `same-sep`: target value in the same file but separate array, i.e., first array includes samples and the second one contains target values.
  evidently, both arrays should have same length and corresponding features and labels for each sample.
```angular2html
f1, f2 = [1,2,3,4,5], [10,20,30,40,50]
l1, l2 = 0, 1
features = [f1, f2]
labels = [l1, l2]
dataset = [features, labels]
``` 

- `same-last`: like `same-sep` both labels and features are in the same file; however, each sample's label comes right
   at the end of array that contains features array. 
```angular2html
features = [1,2,3,4,5]
label = 0
sample = [features, label]
dataset = [sample, sample]
``` 
- name of a separate numpy file (`.npy`,`.npz`) that contains target values.
## Output
Output directory includes splits of test and train data that will be in the same format as input file.

## Workflows
Can be combined with the following apps:
- Post: 
  - Various preprocessing apps (e.g. Normalization, Feature Selection, ...) 
  - Various analysis apps (e.g. Random Forest, Logistic Regression, Linear Regression)

## Config
Use the config file to customize your training. Just upload it together with your training data as `config.yml`
```
fc_cross_validation:
  local_dataset:
    data: data.npy
    target_value: same-sep
    sep: ','
  n_splits: 10
  shuffle: true
  stratify: false
  random_state: null
  split_dir: data
  result:
    train: train.npy
    test: test.npy
```
- `target_value` indicates where labels can be found inside the input data or can be the name of different file, in the 
same directory as input data file, which contains labels. Beware that `target_value` should be string, even if it's number!
e.g., `target_value: '10'` 
- `n_splits`: number of splits to be created using CV.

## Requirements
- pandas
- numpy
- scikit-learn