"""
    FeatureCloud Mean Application
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
from FeatureCloud.engine.app import app_state, AppState, Role, SMPCOperation
from utils import log_data, log_send_data, JsonSerializer
import pandas as pd
import numpy as np
from ..FeatureCloudCustomStates import ConfigState

js_serializer = JsonSerializer()

name = 'mean'


@app_state(name='initial', role=Role.BOTH, app_name=name)
class LocalMean(ConfigState.State):

    def register(self):
        self.register_transition('GlobalMean', Role.COORDINATOR)
        self.register_transition('WriteResults', Role.PARTICIPANT)

    def run(self) -> str or None:
        self.lazy_init()
        self.read_config()
        self.finalize_config()
        self.app.internal['config'] = self.config
        local_mean = []
        dfs = []
        for file_name in self.app.internal['input_files']['data']:
            dfs.append(pd.read_csv(file_name))
        for df in dfs:
            if self.config['axis'] is None:
                local_mean.append(df.mean().mean())
            elif self.config['axis'] == 0:
                local_mean.append(df.mean())
            elif self.config['axis'] == 1:
                local_mean.append([df.mean(), int(self.app.coordinator) * 2 + 100])

        # By default SMPC will not be used, unless end-user asks for it!
        self.app.internal['smpc_used'] = self.config.get('use_smpc', False)
        if self.app.internal['smpc_used']:
            local_mean = js_serializer.prepare(local_mean)
        self.send_data_to_coordinator(data=local_mean,
                                      use_smpc=self.app.internal['smpc_used'])
        log_send_data(local_mean, self.app.log)

        self.update(progress=0.1)
        if self.app.coordinator:
            return 'GlobalMean'
        return 'WriteResults'


@app_state('GlobalMean', Role.COORDINATOR)
class GlobalMean(AppState):

    def register(self):
        self.register_transition('WriteResults', Role.COORDINATOR)

    def run(self) -> str or None:
        global_mean = []
        aggregated_data = self.aggregate_data(operation=SMPCOperation.ADD, use_smpc=self.app.internal['smpc_used'])
        log_data(aggregated_data, self.app.log)
        for split_data in aggregated_data:
            if self.app.internal['config']['axis'] == 1:
                global_mean.append(np.array(split_data[0]) / split_data[1])
            else:
                global_mean.append(np.array(split_data) / len(self.app.clients))
            self.app.internal['smpc_used'] = False
        self.broadcast_data(data=global_mean)
        log_send_data(global_mean, self.app.log)
        return 'WriteResults'


@app_state('WriteResults', Role.BOTH)
class WriteResults(AppState):

    def register(self):
        self.register_transition('terminal', Role.BOTH)

    def run(self) -> str or None:
        aggregated_data = self.await_data(n=1, unwrap=True, is_json=False)
        log_data(aggregated_data, self.app.log)
        for filename, split_data in zip(self.app.internal['output_files']['mean'], aggregated_data):
            f = open(filename, "w")
            f.write(str(split_data))
            f.close()
        return 'terminal'
