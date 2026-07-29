import json

import numpy as np


class NpEncoder(json.JSONEncoder):
    """JSON encoder for numpy datatypes.

    This encoder code is from Jie Yang on Stack Overflow
    (https://stackoverflow.com/users/6683616/jie-yang) in answer
    https://stackoverflow.com/a/57915246.
    """

    def default(self, obj):  # type: ignore
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
