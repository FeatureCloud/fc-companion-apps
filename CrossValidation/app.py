"""
    FeatureCloud Cross Validation Application
    Copyright 2021 Mohammad Bakhtiari, Julian Spath. All Rights Reserved.
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
from FeatureCloud.CustomStates import ConfigState
from FeatureCloud.engine.app import app_state, Role, AppState, LogLevel
from FeatureCloud.engine.app import State as op_state
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, KFold
import os

name = 'fc_cross_validation'

default_config = {
    name: {
        'local_dataset': {
            'data': 'data.csv',
            'target_value': '10',  # should be str
            'sep': ','
        },
        'n_splits': 10,
        'shuffle': True,
        'stratify': False,
        'random_state': None,
        'split_dir': 'data',
        'result': {
            'train': 'train.csv',
            'test': 'test.csv'
        }
    }
}

requirements = ['pandas', 'sklearn']


@app_state(name='initial', role=Role.BOTH, app_name=name)
class LoadAndSplit(ConfigState.State):

    def register(self):
        self.register_transition('WriteResults', Role.BOTH)

    def run(self):
        self.lazy_init()
        self.read_config()
        self.finalize_config()
        self.app.internal['format'] = self.config['local_dataset']['data'].lower().split(".")[-1].strip()
        self.app.internal['sep'] = self.config['local_dataset']['sep'].strip()
        self.app.internal['target'] = self.config['local_dataset']['target_value'].strip()
        df = self.read_data()
        # Creat placeholders for output files
        output_folder = f"{self.output_dir}/{self.config['split_dir']}"
        self.app.internal['output_files'] = {'train': [], 'test': []}
        for i in range(self.config['n_splits']):
            os.makedirs(f"{output_folder}/{i}")
            self.app.internal['output_files']['train'].append(f"{output_folder}/{i}/{self.config['result']['train']}")
            self.app.internal['output_files']['test'].append(f"{output_folder}/{i}/{self.config['result']['test']}")
        self.update(progress=0.1)
        self.app.internal['splits'] = self.create_splits(df)
        self.update(progress=0.5)
        return 'WriteResults'

    def read_data(self):
        file_name = self.app.internal['input_files']['data'][0]
        if self.app.internal['format'] in ["npy", "npz"]:
            df = self.load_numpy_files(file_name)
        elif self.app.internal['format'] in ["csv", "txt"]:
            df = pd.read_csv(file_name, sep=self.config['local_dataset']['sep'])
        else:
            self.app.log(f"{self.app.internal['format']} file types are not supported", LogLevel.ERROR)
            self.update(state=op_state.ERROR)
        return df

    def load_numpy_files(self, file_name):
        ds = np.load(file_name, allow_pickle=True)
        if self.app.internal['format'] == "npz":
            ds = ds['arr_0']
        target_value = self.config['local_dataset'].get('target_value', False)
        if target_value:
            if target_value == 'same-sep':
                return pd.DataFrame({"features": [s for s in ds[0]], "label": ds[1]})
            elif target_value == 'same-last':
                return pd.DataFrame({"features": [s[:-1] for s in ds], "label": [s[-1] for s in ds]})
            elif target_value.strip().split(".")[1].lower() in ['npy', 'npz']:
                labels = np.load(f"{self.input_dir}/{self.config['local_dataset']['target_value']}",
                                 allow_pickle=True)
                return pd.DataFrame({"features": [s for s in ds], "label": labels})
            self.app.log(f"{target_value} is not supported", LogLevel.ERROR)
            self.update(state=op_state.ERROR)
        else:
            self.app.log("For NumPy files, the format of target value should be mentioned through `target_value` "
                         "key in config file", LogLevel.ERROR)
            self.update(state=op_state.ERROR)

    def create_splits(self, data):
        splits = []
        if self.config['stratify'] and (self.config['local_dataset']['target_value'] is not None):
            self.app.log(f'Use stratified kfold cv for label column', LogLevel.DEBUG)
            cv = StratifiedKFold(n_splits=self.config['n_splits'], shuffle=self.config['shuffle'],
                                 random_state=self.config['random_state'])
            y = data.loc[:, self.config['local_dataset']['target_value']]
            data = data.drop(self.config['local_dataset']['target_value'], axis=1)
            for train_indices, test_indices in cv.split(data, y):
                train_df = pd.DataFrame(data.iloc[train_indices], columns=data.columns)
                test_df = pd.DataFrame(data.iloc[test_indices], columns=data.columns)
                splits.append([train_df, test_df])
        else:
            self.app.log(f'Use kfold cv', LogLevel.DEBUG)
            cv = KFold(n_splits=self.config['n_splits'], shuffle=self.config['shuffle'],
                       random_state=self.config['random_state'])
            for train_indices, test_indices in cv.split(data):
                train_df = pd.DataFrame(data.iloc[train_indices], columns=data.columns)
                test_df = pd.DataFrame(data.iloc[test_indices], columns=data.columns)
                splits.append([train_df, test_df])
        return splits


@app_state(name='WriteResults', role=Role.BOTH)
class WriteResults(AppState):
    def register(self):
        self.register_transition('terminal', Role.BOTH)

    def run(self) -> str or None:
        files = zip(self.app.internal['splits'],
                    self.app.internal['output_files']['train'],
                    self.app.internal['output_files']['test'])
        print(files)
        csv_writer = lambda filename, df: df.to_csv(filename, sep=self.app.internal['sep'], index=False)
        np_lambda = lambda filename, df: save_numpy(filename,
                                                    df.iloc[:, 0].to_numpy(),
                                                    df.iloc[:, 1].to_numpy(),
                                                    self.app.internal['target'])
        save = {"npy": np_lambda, "npz": np_lambda, "csv": csv_writer, "txt": csv_writer}
        progress = 0.5
        step = 0.4 / len(self.app.internal['splits'])
        for [train_split, test_split], train_filename, test_filename in files:
            print(train_filename, test_filename)
            save[self.app.internal['format']](train_filename, train_split)
            save[self.app.internal['format']](test_filename, test_split)
            progress += step
            self.update(progress=progress)
        self.update(progress=1.0)
        return 'terminal'


def save_numpy(file_name, features, labels, target):
    if target == "same-sep":
        np.save(file_name, np.array([features, labels]))
    elif target == "same-last":
        samples = [np.append(features[i], labels[i]) for i in range(features.shape[0])]
        np.save(file_name, samples)
    elif target.strip().split(".")[1].lower() == 'npy':
        np.save(file_name, features)
        np.save(target, labels)
    elif target.strip().split(".")[1].lower() in 'npz':
        np.savez_compressed(file_name, features)
        np.savez_compressed(target, labels)
    else:
        return ValueError
