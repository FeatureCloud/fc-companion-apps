# FeatureCloud Companion apps

### Preprocessing and example apps in FeatureCloud platform
Among three major app categories in FeatureCloud, this repository is focused on providing apps for preprocessing purposes.
These apps can be used in a workflow as a companion for one or a few analysis or learning apps. Meanwhile, this repository can be regarded as a good set of example apps in the FeatureCloud platform, which freshly started developers can refer to for learning 
how to implement apps using FeatureCloud library. 

## Easy App development using FeatureCloud
In this repository, we implemented multiple apps in different packages. Each package includes an `app.py` which contains
all the states. Also, each app package includes a `requirements.txt` and `config.yml` file, which are essential to build the
image and run the container, respectively. For building the container, each app should contain specific files, which mostly share the same info,
and a list of required libraries specific to apps. Here, to simplify it, we included a general [requirements](requirements.txt) covering all the required libraries for all the apps. Therefore, once you want to build the 
container, you just need to import `app` from the app package that you want to use. Importing the app is enough to register
all the states and transitions that are supposed to carry on the app's task. Once you want to run the app, you should 
provide a config file. In a workflow with multiple apps, each app should have its own config file; we simply provide on general [config file](config.yml) for all apps and pass it from one app to another. In fact, ![ConfigState]()
automatically clones the config file into the output directory to provide it for the following app. 

## Companion Apps
Generally, FeatureCloud apps are categorized into preprocessing, Analysis and learning apps, and postprocessing.
This repository only includes preprocessing apps. 

### preprocessing apps
Once end-users use analysis or learning apps in a workflow, they most likely need to preprocess the data. In many cases, the same preprocessing steps can be applied to multiple tasks' data. Therefore, it is reasonable to introduce preprocessing apps to provide acceptable output files for analysis or learning apps. In that regard, most companion apps in this repository support the following files:
- CSV: it is a very commonly used format in the machine learning and data analysis community. All apps that accept CSV files also 
support different delimiters.
- TXT is another common file type to store and transfer data that will be treated as a CSV file with a comma separator.
- Numpy files: Due to the popularity of the NumPy library and its role in other viral libraries like Sklearn or PyTorch,
All the apps support NumPy files, both compressed and uncompressed ones.

Once users begin to experiment with the FeatureCloud platform, they may want to use dummy data at first to familiarize themselves with 
the platform and libraries. One option would be to employ [Data Distributor](/DataDistributor/README.md) as the first app
in a workflow to distribute centralized data among clients. Once the data and config files are ready in clients, one can use     
[Cross Validation](/CrossValidation/README.md) app to split the local dataset into multiple splits where each split includes a train and test set.
Cross-validation is a common practice to make sure that the results of the learning app are not accidental. Some applications use images 
as input to be stored in different datasets. In such cases, the [Image Loader](/ImageLoader/README.md) app can load and store all the
images in a Numpy file. After loading images, users can employ [Image Normalization](/ImageNormalization/README.md) app to normalize local datasets across 
image channels. Overall, there can be different workflows to use companion apps.
For instance :

![Workflow](/data/images/Workflow.png)

Two clients, i.e., coordinator and participant, collaborate in this federated workflow that includes six apps; 
Any of possible classification and evaluation apps in FeatureCloud ![AI-Store](https://featurecloud.ai/ai-store) 
can be used in this workflow.

## Exemplary app in FeatureCloud 
To exemplify and provide FeatureCloud users with apps
that cover preliminary operations in FC workflow, this repository includes different apps that utilize various features
of FC platform. 
### Broadcasting data to all clients:
[Data Distributor](/DataDistributor/README.md), [Image Normalization](/ImageNormalization/README.md), and 
[Mean](/Mean/README.md) apps.

### Secure Aggregation using SMPC
[Image Normalization](/ImageNormalization/README.md) and [Mean](/Mean/README.md) apps.

### Local Computation and operations without Communication
[Cross Validation](/CrossValidation/README.md) and [Image Loader](/ImageLoader/README.md) apps.

## ConfigSate
[`ConfigSate`](/FeatureCloudCustomStates/README.md) can be optionally used as the first state, `initial` state,
in the app which reads the config file and interprets it to provide necessary information
for following states to facilitate data I/O, splits, and serialization. 

