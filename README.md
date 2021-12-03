# FeatureCloud Companion apps

### Preprocessing and example apps in FeatureCloud platform
Among three major app categories in FeatureCloud, this repository is focused to provide apps for preprocessing purposes.
These apps can be used in a workflow as a companion for one or few analysis or learning apps. Meanwhile, this repository can be regarded as a 
good set of example apps in FeatureCloud platform which freshly started developers can refer to for learning 
how to implement apps using FeatureCloud library. 

## Easy App development using FeatureCloud
In this repository we implemented multiple apps that in different packages. each package includes an `app.py` which contains
all the states. Also, each app package includes a `requirements.txt` and `config.yml` file which are essential to build the
image and run the container, respectively. To build the container, each app should contain specific files, which mostly share same info,
and a list of requirement libraries that are specific to apps. Here to make it simple we included a general 
[requirements](requirements.txt) that covers all the required libraries for all the apps. Therefore, once you want to build the 
container you just need to import `app` from the app package that you want to use. Importing the app is enough to register
all the states and transitions that are supposed to carry on the app's task. Once you want to run the app, you should 
provide a config file. In a workflow with multiple apps, each app should have its own config file and to make it simple,
we just provide on general [config file](config.yml) for all apps and pass it from one app to another. In fact, ![ConfigState]()
automatically clones the config file into the output directory to provide it for the following app. 

## Companion Apps
Generally FeatureCloud apps are categorized into preprocessing, Analysis and learning apps, and postprocessing.
This repository only includes preprocessing apps. 

### preprocessing apps
Once end-users use analysis or learning apps in a workflow it's most likely they need to pre-process the data. In many cases 
the same preprocessing steps can be applied on the data for multiple tasks. Therefore, it is reasonable to introduce pre-processing apps
that can provide acceptable output files for major analysis or learning apps. In that regard, most comapnion apps in this repository support
following files:
- CSV: it is a very commonly used format in Machine learning and data analysis community. All apps who accept CSV files also 
support different delimiters.
- TXT: another common file type to store and transfer data which will be treated as a CSV file with comma separator.
- Numpy files: Due to the popularity of Numpy library and its role in other highly popular libraries like Sklearn or PyTorch,
All the apps support numpy files, both compressed and uncompressed ones.

Once users began to experiment with FeatureCloud platform they may want to use dummy data at first to familiarize themselves with 
the platform and libraries. One option would be employing [Data Distributor](/DataDistributor/README.md) app as the first app
in a workflow to distribute a centralized data among clients. Once the data and config files are ready in clients, one can use     
[Cross Validation](/CrossValidation/README.md) app to split the local dataset into multiple splits where each split includes a train and test set.
Cross validation is a common practice to make sure that results of learning app are not accidental. Some applications use images 
as input where they can be stored in different datasets. In such cases, [Image Loader](/ImageLoader/README.md) app can load and store all the
images in a Numpy file. After loading images, users can employ [Image Normalization](/ImageNormalization/README.md) app to normalize local datasets across 
image channels. Overall, there can be different workflows to use companion apps.
For instance :

![Workflow](/data/images/Workflow.png)

Two clients, coordinator and participant, collaborate in this federated worflow that includes six apps; 
Any of possible classification and evaluation apps in FeatureCloud ![AI-Store](https://featurecloud.ai/ai-store) 
can be used in this workflow.

## Exemplary app in FeatureCloud 
For the purpose of exemplifying and providing FeatureCloud users with apps
that cover preliminary operations in FC workflow, this repository includes different apps that utilize various features
of FC platform. 
### Broadcasting data to all clients:
[Data Distributor](/DataDistributor/README.md), [Image Normalization](/ImageNormalization/README.md), and 
[Mean](/Mean/README.md) apps.

### Secure Aggregation using SMPC
[Image Normalization](/ImageNormalization/README.md) and [Mean](/Mean/README.md) apps.

### Local Computation and operations without Communication
[Cross Validation](/CrossValidation/README.md) and [Image Loader](/ImageLoader/README.md) apps.
