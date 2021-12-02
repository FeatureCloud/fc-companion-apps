import numpy as np
from utils import load_numpy


def read_file(filename, target):
    """ load a numpy file and compute mean and std. for each channel
    Parameters
    ----------
    filename: str
    target: str
    Returns
    -------
    """
    data = load_numpy(filename)
    if target == "same-sep":
        x, y = data
        x = np.array(list(x))
    elif target == 'same-last':
        x = [s[-1] for s in data]
        y = [s[-1] for s in data]
    elif '.npy' in target or '.npz' in target:
        x = data
        y = np.load(target, allow_pickle=True)
    x = np.array(list(x))
    sample_shape = x[0].shape[1:]
    if min(sample_shape) > 3:
        x = np.expand_dims(x, axis=-1)
    mean = np.mean(x, axis=tuple(range(x.ndim - 1)))
    std = np.std(x, axis=tuple(range(x.ndim - 1)))
    return x, y.tolist(), mean, std
