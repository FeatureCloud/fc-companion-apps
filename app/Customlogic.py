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
from .logic import AppLogic, bcolors
import bios
import os


class CustomLogic(AppLogic):
    """ Subclassing AppLogic for overriding specific methods
        to implement the deep learning application.

    Attributes
    ----------
    config_settings: dict
    data: dict

    Methods
    -------
    init_state()
    read_input()
    wait_for_data()
    broadcast_data()
    write_results(m)
    final_step()

    """

    def __init__(self):
        super(CustomLogic, self).__init__()

        # Shared parameters and data
        self.config_settings = {}
        self.data = {}

        # Define States
        self.states = {"Initializing": self.init_state,
                       "Read input data and Config file": self.read_input,
                       "Waiting for Config file and data": self.wait_for_data,
                       "Broadcasting Config file and data": None,
                       "Writing Results": None,
                       "Finishing": self.final_step
                       }
        self.state = 'Initializing'

    def init_state(self):
        if self.id is not None:  # Test if setup has happened already
            if self.coordinator:
                self.state = "Read input data and Config file"
            else:
                self.state = "Waiting for Config file and data"

    def read_input(self):
        self.state = "Broadcasting Config file and data"

    def wait_for_data(self):
        self.progress = 'wait for init parameters from server'
        decoded_data = self.wait_for_server()
        if decoded_data is not None:
            print(f"{bcolors.SEND_RECEIVE} Received Init Config file and data from coordinator. {bcolors.ENDC}")
            data = decoded_data[0]
            self.config_settings = {data.index[i]: ast.literal_eval(data.config.values[i]) for i in range(len(data))}
            print(self.config_settings)
            self.data = decoded_data[1]
            self.state = "Writing Results"

    def broadcast_data(self):
        config = pd.DataFrame({'config': self.config_settings})
        self.broadcast([config, self.data])
        self.state = "Writing Results"

    def write_results(self):
        if self.coordinator:
            self.data_incoming.append('DONE')
            self.state = "Finishing"
        else:
            self.data_outgoing = 'DONE'
            self.status_available = True
            self.state = None

    def final_step(self):
        self.progress = 'finishing...'
        if len(self.data_incoming) == len(self.clients):
            self.status_finished = True
            self.state = None