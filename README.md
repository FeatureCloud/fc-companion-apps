# FeatureCloud Companion apps

### Preprocessing and example apps in FeatureCloud platform
Among three major app categories in FeatureCloud, this repository is focused to provide apps for pre-processing and post-processing purposes.
These apps can be used in a workflow as a companion for one or few analysis or learning apps. Meanwhile, this repository can be regarded as a 
good set of example apps in FeatureCloud platform which freshly started developers can refer to for learning 
how to implement apps using FeatureCloud library. 

## Easy App development using FeatureCloud
running apps in a workflow:
[requirements](requirements.txt)
[config file](config.yml)

## Companion Apps
Generally FeatureCloud apps are categorized into Pre-processing, Analysis and learning apps, and Post-processing.
This repository only includes pre/post-processing apps. 

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

## Exemplary app implantation in FeatureCloud 
For the purpose of exemplifying and providing FeatureCloud users with apps
that cover preliminary operations in FC workflow, `FeatureCloud.apps` package 
contains followings apps:
[CrossValidation](/CrossValidation/README.md)
[DataDistributor](/DataDistributor/README.md)
[ImageLoader](/ImageLoader/README.md)
[ImageNormalization](/ImageNormalization/README.md)
[Mean](/Mean/README.md)

## Developing Apps using FeatureCloud library 
In general, for developing apps in FeatureCloud platform, apps should be able to communicate with FeatureCloud controller.
For this purpose, app-developers have multiple options, that all includes employing `FeatureCloud.engine` package which 
provides the basic means. In the most simplistic way, they can extend `FeatureCloud.engine.app.State` class to define new 
custom states, use `app_state` handler to register their state inside the app. Beware that all apps only use the default 
instance of `FeatureCloud.engine.app.App` which is `FeatureCloud.engine.app.app` and for customizing it define and register 
some states. FeatureCloud apps can support different states and various communications; moreover, they can be used inside 
a workflow in conjunction with other apps. Inside each workflow, every app gets the input files from output of previous
app in the workflow, except for the fist one, which gets data from end-users. Accordingly, there can be a convention that 
facilitate providing acceptable results for other accompanying apps in a workflow and also, easing the development. Therefore,
we introduce a convention that is recommended to leverage for facilitating debugging and readability purposes.
This convention, to some extent, can be ignored by developers, and replaced with anther one. In the followings, we elaborate
different parts that should be included in FeatureCloud apps and how we are going to handle them.

### Defining a custom app
App states can be defined in any place, but conventionally, we recommend including all the state definition in a specific file.
This file can contain other app parts than states, which increases the readability of apps and facilitate their usage.

### App name
For building the app docker image and running it in FeatureCloud platform, each app should have a name, and we recommend following 
convention for it:
- app name should include no `space` character and better to use `_` as delimiter.
- 

### Config file
Each app has some input parameters that brings some flexibility to end-users for executing it on different data or settings.
Such parameters should be included in a config file conventionally named `config.yml`. To inform end-users of parameters
and corresponding value options, app-developers could conventionally define `default_config` dictionary witch includes the name 
of app as the only key, which includes a nested dictionary for parameters. Beware that once apps are used ine the workflow,
all config files should be included inside same `config.yml` file and passed from one app to the next one. So, to distinguish
between app configs, we can use their name. 

```angular2html
default_config = {
    name: {
        'local_dataset': {
            'data': 'data.csv',
            'task': 'classification',
            'target_value': 'label',
            'sep': ','
        },
        'sampling': {
            'type': 'Non-IID',
            'non_iid_ness': 1
        },
        'result': {
            'data': 'data.csv'
        }
    }
}
```
In this example there are `local_dataset` and `result` dictionaries, which can be necessary for almost all apps, while includes
app specific details. For instance, `task`, `target_values`, and `sep` keys are specifically useful for DataDistributor app
to know how to handle the input data. Even though each config file could include arbitrary key/value pairs, there are  share parts can be found in all apps.
Here we cover how conventionally we can cover those parts.

#### Local Datasets
Each app receives some local data from clients that should be in same extension and, to some degree, in a specific format.
Currently, all input data, in different clients, should have same name and extension. Therefore, cconvetionally we define 
`local_dataset` as dictionary that contains each data part required by the app and its corresponding file in clients local 
space.

#### Result
All or parts of results of an app can be used by another one in a workflow, and it should be in specific acceptable format 
the next app. Therefore, `result` s another dictionary in `defualt_config` to contain expected output file and their exact name and 
format. Keys are indicating the output, which helps current app to know what should be exact name of output.

#### SMPC
SMPC module can be used in discretion of app developers to straighten user-privacy. In FeatureCloud platform,
to provides reasonable flexibility, app-developers can delegate the decision about usage of SMPC, and also, it's parameters,
to the end-users. In that case, config file could also include an `use_smpc` key with boolean value to indicate the decision of
end-users. Beware that all clients, for specific communication, should have a consistent decision about using SMPC component.

#### Logic
Once the app container is built and ran, clients data will be copied inside the container, to be processed. Sometimes
there is a directory that includes multiple nested directories and/or files as input. For covering that scenarios,
conventionally, developers can include `logic` dictionary inside the config file that includes following keys:
- `mode`: value should indicate either `directory` or `file` as type of input files. Conventionally, each data that was
named in `local_dataset` can be expected as a single file or a directory including multiple splits of that single file.
A clear case of `directory` mode is CrossValidation app, which splits clients data into multiple splits.
- `dir`: The value should be either `.` that indicates the file name can be found in current directory, inside docker container, 
or name of the directory containing the input files. 


