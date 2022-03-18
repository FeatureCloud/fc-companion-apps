import numpy as np
import pandas as pd
from FeatureCloud.app.engine.app import LogLevel, app
from FeatureCloud.app.api.http_ctrl import api_server
from FeatureCloud.app.api.http_web import web_server
from bottle import Bottle


def run(host='localhost', port=5000):
    """ run the docker container on specific host and port.

    Parameters
    ----------
    host: str
    port: int

    """

    app.register()
    server = Bottle()
    server.mount('/api', api_server)
    server.mount('/web', web_server)
    server.run(host=host, port=port)


def save_numpy(file_name, features, labels, target):
    format = file_name.strip().split(".")[1].lower()
    save = {"npy": np.save, "npz": np.savez_compressed}
    if target == "same-sep":
        save[format](file_name, np.array([features, labels]))
    elif target == "same-last":
        samples = [np.append(features[i], labels[i]) for i in range(features.shape[0])]
        save[format](file_name, samples)
    elif target.strip().split(".")[1].lower() == 'npy':
        np.save(file_name, features)
        np.save(target, labels)
    elif target.strip().split(".")[1].lower() in 'npz':
        np.savez_compressed(file_name, features)
        np.savez_compressed(target, labels)
    else:
        return None


def load_numpy(file_name):
    ds = np.load(file_name, allow_pickle=True)
    format = file_name.strip().split(".")[1].lower()
    if format == "npz":
        return ds['arr_0']
    return ds


def sep_feat_from_label(ds, target):
    if target == 'same-sep':
        return pd.DataFrame({"features": [s for s in ds[0]], "label": ds[1]})
    elif target == 'same-last':
        return pd.DataFrame({"features": [s[:-1] for s in ds], "label": [s[-1] for s in ds]})
    elif target.strip().split(".")[1].lower() in ['npy', 'npz']:
        labels = load_numpy(target)
        return pd.DataFrame({"features": [s for s in ds], "label": labels})
    else:
        return None


def log_clients_data(clients_data, log_func):
    """ Logs the gathered data by the coordinator regarding the SMPC module and data type

    Returns
    -------

    """
    log_func("clients' data arrived", LogLevel.DEBUG)
    log_func(f"Number of clients: {len(clients_data)}", LogLevel.DEBUG)
    log_func("Recieved data from clients: Client_ID: type, length", LogLevel.DEBUG)
    for client_data in clients_data:
        log_func(f"\t{client_data[1]}: {type(client_data[0])},"
                 f" {len(client_data[0]) if hasattr(client_data[0], '__len__') else 1}",
                 LogLevel.DEBUG)


def log_data(data, log_func):
    """ logs the data based on its type, length, and value

    Parameters
    ----------
    data: str
    title: str
    """
    log_func(f"Data:\n"
             f"\tType: {type(data)}\n"
             f"\tlength: {len(data)}", LogLevel.DEBUG)
    for i, d in enumerate(data):
        if hasattr(d, "__len__") and len(d) > 1:
            log_func(f"\t{i}: Length= {len(d)}", LogLevel.DEBUG)
        else:
            log_func(f"\t{i}: Data= {d}", LogLevel.DEBUG)


def log_send_data(data, log_func):
    """ Logs data in terms of legth, type, and value

        Parameters
        ----------
        data: list
        """
    log_func(f"Sending data to coordinator", LogLevel.DEBUG)
    log_func(f"Type: {type(data)}\n"
             f"length: {len(data)}", LogLevel.DEBUG)
    for i, d in enumerate(data[:3]):
        if hasattr(d, '__len__'):
            log_func(f"\t{i} >>> Length: {len(d)}", LogLevel.DEBUG)
        else:
            log_func(f"\t{i} >>> Data: {d}", LogLevel.DEBUG)


class JsonSerializer:
    """
    A serilizer to automatically convert all NumPy arrays, Panda DataFrames, and Pandas Series
    in a nested data structure into lists. All list, tuples, and dictionaries in the submitted data
    will remain untouched
    """

    def __init__(self):
        self.encoder = {pd.DataFrame: pd.DataFrame.to_numpy,
                        pd.core.series.Series: pd.Series.tolist,
                        np.ndarray: self.encode_numpy,
                        dict: self.encode_dict,
                        list: self.encode_list}

    def prepare(self, data):
        if type(data) in self.encoder:
            return self.encoder[type(data)](data)
        return data

    def encode_list(self, data):
        l = []
        for item in data:
            l.append(self.prepare(item))
        return l

    def encode_dict(self, data):
        return {k: self.prepare(v) for k, v in data.items()}

    def encode_numpy(self, data):
        l = []
        for item in data.to_list():
            l.append(self.prepare(item))
        return l
