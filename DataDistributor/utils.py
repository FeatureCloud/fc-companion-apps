"""
    FeatureCloud Application
    Copyright 2021 Mohammad Bakhtiari. All Rights Reserved.
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def supervised_iid_sampling(df, clients):
    """
        IID sampling of data regardless of number of class labels
        Curtrently it supports classification data
         (i.e. each sample should include an arbitrary number of features
            and a single class label from a finite discrete set of lables)

    Parameters
    ----------
    df: pandas.DataFrame
        a dataframe including features and labels of the samples in the dataset
    clients: list
        ID of clients that data should be distributed among them

    Returns
    -------
    clients_data: pandas.DataFrame
        a dataframe including ASSIGNED_CLIENT column to indicate the corresponding client
            that the sample should be assigned.
    """
    labels = df.label.unique()
    clients_data = pd.DataFrame({})
    for label in labels:
        target_label = df[df.label == label]
        proportion = len(target_label) // len(clients)
        for idx, client in enumerate(clients):
            if idx == len(clients) - 1:
                drop_indices = target_label.index.values.tolist()
            else:
                drop_indices = np.random.choice(target_label.index.values.tolist(), proportion, replace=False)
            data = target_label.loc[drop_indices]
            data['ASSIGNED_CLIENT'] = client
            clients_data = clients_data.append(data, ignore_index=True)
            target_label = target_label.drop(drop_indices)
    return clients_data


def flatten(df_lists):
    temp = []
    for df_list in df_lists:
        temp += df_list
    return temp


def noniid_sampling(df, clients, noniid):
    """ NonIID sampling of data to simulate different levels of data heterogeneity
        across clients. An arbitrary number of clients and class labels are supported.
        in case of having less clients than allowed threshold to distribute samples
        of individual classes, the maximum number of available clients will get the samples.

    Parameters
    ----------
    df: pandas.DataFrame
        a dataframe including features and labels of the samples in the dataset
    clients: list
        ID of clients that data should be distributed among them
    noniid: int
        number of clients that have access to samples of a specific class labels.
        In other words, it indicates samples of each class can be found in how many clients.

    Returns
    -------
    clients_data: pandas.DataFrame
        a dataframe including ASSIGNED_CLIENT column to indicate the corresponding client
            that the sample should be assigned.
    """
    labels = df.label.unique()
    all_splits = [[] for _ in range(noniid)]
    for label in labels:
        target_label = df[df.label == label]
        proportion = len(target_label) // noniid
        for i in range(noniid):
            if i == noniid - 1:
                drop_indices = target_label.index.values.tolist()
            else:
                drop_indices = np.random.choice(target_label.index.values.tolist(), proportion, replace=False)
            data = target_label.loc[drop_indices]
            all_splits[i].append(data)
            target_label = target_label.drop(drop_indices)
    splits = flatten(all_splits)
    clients_data = pd.DataFrame([], columns=df.columns)
    counter = 0
    n_labels_for_assign = len(labels) * noniid // len(clients)
    extras = len(labels) * noniid % len(clients)
    for client in clients:
        for _ in range(n_labels_for_assign):
            data = splits[counter]
            data['ASSIGNED_CLIENT'] = client
            clients_data = clients_data.append(data, ignore_index=True)
            counter += 1
        if extras > 0:
            data = splits[counter]
            data['ASSIGNED_CLIENT'] = client
            clients_data = clients_data.append(data, ignore_index=True)
            counter += 1
            extras -= 1
    return clients_data


def plot_clients_data(df, path):
    """

    Parameters
    ----------
    df: pandas.DataFrame
    path: str

    """
    ax = sns.countplot(data=df, hue='label', x='ASSIGNED_CLIENT')
    ax.legend(bbox_to_anchor=(0.99, 1.05))
    for v in df.ASSIGNED_CLIENT.unique()[:-1]:
        plt.axvline(x=v, color='black', linestyle='dotted')
    plt.savefig(f'{path}/hist.png')


def unsupervised_iid_sampling():
    raise NotImplementedError


def log_dataframe(df):
    msg = f"Pandas DataFrame: \n" \
          f"Number of rows: {len(df)}\n" \
          f"Number of Columns: {len(df.columns)} \n"
    if len(df.columns.values) > 8:
        for c in df.columns.values[:5]:
            msg += f"\t{c}\n"
        msg += "\t.\n\t.\n\t.\n"
        for c in df.columns.values[-3:]:
            msg += f"\t{c}\n"
    else:
        for c in df.columns.values[:5]:
            msg += f"\t{c}\n"
    return msg
