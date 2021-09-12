"""
    FeatureCloud Experiment Application

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
import pandas as pd

from .logic import bcolors
from .Customlogic import CustomLogic
import bios
import os
import shutil
import numpy as np
from .utils import load_dataset, supervised_iid_sampling, noniid_sampling, unsupervised_iid_sampling, plot_clients_data


class Experiment(CustomLogic):
    """
    Attributes
    ----------
    ds_conf: dict
    sampling_conf: dict
    df: pandas.DataFrame

    Methods
    -------
    read_config(config_file)
    read_input()
    broadcast_data()
    sample_dataset()
    write_results()
    """

    def __init__(self):
        super(Experiment, self).__init__()

        #   Configs
        self.ds_conf = {}
        self.sampling_conf = {}

        #   Models & Parameters
        self.df = pd.DataFrame({})

        #  Update States Functionality
        self.states["Broadcasting Config file and data"] = self.broadcast_data
        self.states["Writing Results"] = self.write_results

    def read_config(self, config_file):
        """

        Parameters
        ----------
        config_file: string
            path to the config.yaml file!

        """
        self.config_settings = bios.read(config_file)
        config = self.config_settings['fc_experiment']
        self.ds_conf = config['dataset']
        self.ds_conf['task'] = self.ds_conf['task'].lower()
        self.ds_conf['target_value'] = self.ds_conf['target_value'].lower()
        self.ds_conf['format'] = self.ds_conf['filename'].strip().split(".")[-1].lower()
        if not self.ds_conf['format'] in ['txt', 'npy', 'csv']:
            raise NotImplementedError(f"Unsupported {self.ds_conf['format']} file extension!")
        self.sampling_conf = config['sampling']
        self.sampling_conf['type'] = self.sampling_conf['type'].lower()
        if not self.sampling_conf['type'] in ['non-iid', 'noniid', 'non_iid', 'iid']:
            raise NotImplementedError(f"Unsupported {self.sampling_conf['type']} type!")

    def read_input(self):
        self.progress = "Read data"
        self.read_config(self.INPUT_DIR + '/config.yml')
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        shutil.copyfile(self.INPUT_DIR + '/config.yml', self.OUTPUT_DIR + '/config.yml')
        print(f'{bcolors.STATE}Read config file.{bcolors.ENDC}', flush=True)
        ds_file = self.INPUT_DIR + "/" + self.ds_conf['filename']
        print(f"{bcolors.VALUE}Reading {ds_file} ...{bcolors.ENDC}")
        self.df = load_dataset(self.ds_conf, self.INPUT_DIR)
        if self.sampling_conf['type'] in ['non-iid', 'noniid', 'non_iid']:
            labels = self.df.label.unique()
            assert 0 < int(self.sampling_conf['non_iid_ness']) <= len(labels), \
                f"{bcolors.FAIL}Level of Non-IID-ness is restricted to the number of classes!\n" \
                f"{bcolors.VALUE}Number of labels: {len(labels)}\n" \
                f"Non-IID-ness: {self.sampling_conf['non_iid_ness']}{bcolors.ENDC}"

        super(Experiment, self).read_input()

    def broadcast_data(self):
        self.progress = "Sample the dataset and broadcast"
        self.data = self.sample_dataset()
        super(Experiment, self).broadcast_data()

    def sample_dataset(self):
        self.df['ASSIGNED_CLIENT'] = None
        if self.ds_conf['task'] == 'classification':
            if self.sampling_conf['type'] == 'iid':
                clients_data = supervised_iid_sampling(self.df, self.clients)
            else:
                clients_data = noniid_sampling(self.df, self.clients, self.sampling_conf['non_iid_ness'])
        else:
            clients_data = unsupervised_iid_sampling()
        return clients_data

    def write_results(self):
        self.progress = "write results"
        plot_clients_data(self.data, self.OUTPUT_DIR)
        data = self.data[self.data.ASSIGNED_CLIENT == self.id].drop(columns='ASSIGNED_CLIENT')
        if not self.coordinator:
            bios.write(f"{self.OUTPUT_DIR}/config.yml", self.config_settings)
            self.ds_conf = self.config_settings['fc_data_distributor']['dataset']
        if self.ds_conf['format'] == 'npy':
            features = data.features.values
            labels = data.label.values
            if self.ds_conf['target_value'] == "same-sep":
                temp = np.array([features, labels])
                np.save(f"{self.OUTPUT_DIR}/{self.ds_conf['filename']}", temp)
            elif self.ds_conf['target_value'] == "same-last":
                samples = []
                for i in range(features.shape[0]):
                    samples.append(np.append(features[i], labels[i]))
                np.save(f"{self.OUTPUT_DIR}/{self.ds_conf['filename']}", samples)
            elif self.ds_conf['target_value'].strip().split(".")[1].lower() == 'npy':
                np.save(f"{self.OUTPUT_DIR}/{self.ds_conf['filename']}", data.features.values)
                np.save(f"{self.OUTPUT_DIR}/{self.ds_conf['target_value']}", data.label.values)
            else:
                raise ValueError(f"Oops! {self.ds_conf['target_value']} is not a supported value for target_value.")
        else:
            data.rename(columns={'label': self.ds_conf['target_value']}, inplace=True)
            data.to_csv(f"{self.OUTPUT_DIR}/{self.ds_conf['filename']}", sep=self.ds_conf['sep'], index=False)
        super(Experiment, self).write_results()


logic = Experiment()
