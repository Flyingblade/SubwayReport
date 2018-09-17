import json
import numpy as np
import datetime as dt
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dt.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return super(MyEncoder, self).default(obj)