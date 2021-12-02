"""
    FeatureCloud Image Normalization Application
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
import copy
import os.path
from FeatureCloud.CustomStates import ConfigState
from FeatureCloud.engine.app import app_state, AppState, Role, LogLevel, SMPCOperation
from FeatureCloud.engine.app import State as op_state
import numpy as np
from utils import save_numpy
from .utils import read_file

name = 'fc_image_normalization'

default_config = {
    name: {
        'local_dataset': {
            'train': 'train.npy',
            'test': 'test.npy',
            'target_value': 'same-sep'
        },
        'method': 'variance',
        'logic': {
            'mode': 'file',
            'dir': '.'
        },
        'use_smpc': False,
        'result': {
            'train': 'train.npy',
            'test': 'test.npy'
        }
    }
}

requirements = ['matplotlib', 'seaborn']


@app_state(name='initial', role=Role.BOTH, app_name=name)
class LocalStats(ConfigState.State):

    def register(self):
        self.register_transition('WriteResults', Role.PARTICIPANT)
        self.register_transition('GlobalStats', Role.COORDINATOR)

    def run(self):
        self.lazy_init()
        self.read_config()
        self.finalize_config()
        self.update(progress=0.1)
        self.app.internal['method'] = self.config['method']
        self.app.internal['target_value'] = self.config['local_dataset']['target_value']
        stats = self.read_files()
        self.app.internal['smpc_used'] = self.config.get('use_smpc', False)
        self.send_data_to_coordinator(data=stats, use_smpc=self.app.internal['smpc_used'])
        self.update(progress=0.3)
        if self.app.coordinator:
            return 'GlobalStats'
        return 'WriteResults'

    def read_files(self):
        local_stats = []
        self.app.internal['x_train'], self.app.internal['y_train'] = [], []
        self.app.internal['x_test'], self.app.internal['y_test'] = [], []
        splits = zip(self.app.internal['input_files']['train'], self.app.internal['input_files']['test'])
        for split_train_file, split_test_file in splits:
            if not os.path.isfile(split_train_file):
                self.app.log(f"File not found:\n{split_train_file}", LogLevel.ERROR)
                self.update(state=op_state.ERROR)
            x_train, y_train, mean_train, std_train = read_file(split_train_file,
                                                                self.config['local_dataset']['target_value'])
            n_train_samples = len(x_train)
            mean_train *= n_train_samples
            std_train *= n_train_samples
            self.app.internal['x_train'].append(x_train)
            self.app.internal['y_train'].append(y_train)
            if not os.path.isfile(split_test_file):
                self.app.log(f"File not found:\n{split_test_file}"
                             f"\nNo test set is provided!", LogLevel.DEBUG)
                mean_test, std_test = copy.deepcopy(mean_train), copy.deepcopy(std_train)
                x_test, y_test = [], []
            else:
                x_test, y_test, mean_test, std_test = read_file(split_test_file)
            n_test_samples = len(x_test)
            mean_test *= n_test_samples
            std_test *= n_test_samples

            self.app.internal['x_test'].append(x_test)
            self.app.internal['y_test'].append(y_test)
            local_stats.append([[n_train_samples, mean_train.tolist(), std_train.tolist()], [n_test_samples, mean_test.tolist(), std_test.tolist()]])
        return local_stats

@app_state(name="GlobalStats", role=Role.COORDINATOR)
class GlobalStats(AppState):
    def register(self):
        self.register_transition('WriteResults', Role.COORDINATOR)

    def run(self):
        aggregated_stats = self.aggregate_data(operation=SMPCOperation.ADD, use_smpc=self.app.internal['smpc_used'])
        print(aggregated_stats)
        self.update(progress=0.4)
        global_stats = []
        if self.app.internal['method'] == "variance":
            for train_split, test_split in aggregated_stats:
                n_train_samples, train_mean, train_std  = train_split
                n_test_samples, test_mean, test_std = test_split
                if n_train_samples != 0:
                    train_mean = np.array(train_mean) / n_train_samples
                    train_std = np.array(train_std) / n_train_samples
                else:
                    train_mean = np.array(train_mean) * 0
                    train_std = np.array(train_std) * 0
                if n_test_samples != 0:
                    test_mean = np.array(test_mean) / n_test_samples
                    test_std = np.array(test_std) / n_test_samples
                else:
                    test_mean = np.array(test_mean) * 0
                    test_std = np.array(test_std) * 0
                global_stats.append([train_mean, train_std, test_mean, test_std])
            self.broadcast_data(data=global_stats)
        else:
            self.app.log(f"{self.app.internal['method']} was not implemented as a normalization method.",
                         LogLevel.ERROR)
            self.update(state=op_state.ERROR)
        self.update(progress=0.5)
        return 'WriteResults'


@app_state(name='WriteResults', role=Role.BOTH)
class WriteResults(AppState):
    def register(self):
        self.register_transition('terminal', Role.BOTH)

    def run(self) -> str:
        global_stats = self.await_data(n=1, unwrap=True, is_json=False)
        progress = 0.5
        step = 0.5 / len(global_stats)
        for i, split_stats in enumerate(global_stats):
            x_train, x_test = \
                self.local_normalization(self.app.internal['x_train'][i], self.app.internal['x_test'][i], split_stats)
            self.write_results(x_train, x_test, i)
            progress += step
            self.update(progress=progress)
        self.update(progress=1.0)
        return 'terminal'

    def local_normalization(self, x_train, x_test, global_stats):
        if self.app.internal['method'] == "variance":
            # normalized_x_train = np.subtract(x_train, global_stats["train_mean"]) / global_stats["train_std"]
            normalized_x_train = np.subtract(x_train, global_stats[0]) / global_stats[1]
            if np.size(x_test) != 0:
                # normalized_x_test = np.subtract(x_test, global_stats["test_mean"]) / global_stats["test_std"]
                normalized_x_test = np.subtract(x_test, global_stats[2]) / global_stats[3]
            else:
                normalized_x_test = np.array([])
            return normalized_x_train.tolist(), normalized_x_test.tolist()

        self.app.log(f"{self.conmethod} was not implemented as a normalization method.", LogLevel.ERROR)
        self.update(state=op_state.ACTION)

    def write_results(self, x_train, x_test, i):
        save_numpy(file_name=self.app.internal['output_files']['train'][i],
                   features=x_train,
                   labels=self.app.internal['y_train'][i],
                   target=self.app.internal['target_value'])
        if np.size(x_test) != 0:
            save_numpy(file_name=self.app.internal['output_files']['test'][i],
                       features=x_test,
                       labels=self.app.internal['y_test'][i],
                       target=self.app.internal['target_value'])
