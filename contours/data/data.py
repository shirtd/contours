import matplotlib.pyplot as plt
import numpy as np
import os, json


class Data:
    def __init__(self, data, name, folder, config=None):
        self.data, self.name, self.folder = data, name, folder
        self.config = {} if config is None else config
    def save_json(self, config=None):
        config = {**self.config, **({} if config is None else config)}
        config = {k : v.tolist() if isinstance(v, np.ndarray) else v for k,v in config.items()}
        json_file = os.path.join(self.folder, f'{self.name}.json')
        # print(f'saving {json_file}')
        with open(json_file, 'w') as f:
            json.dump(config, f, indent=2)
    def save_data(self, data=None):
        if data is None:
            data = self.data
        file_name = os.path.join(self.folder, f'{self.name}.csv')
        print(f'saving {file_name}')
        np.savetxt(file_name, data)
    def save(self, data=None, config=None):
        if not os.path.exists(self.folder):
            print(f' mkdir {self.folder}')
            os.makedirs(self.folder)
        self.save_json(config)
        self.save_data(data)
    def save_plot(self, folder='./', dpi=300, tag=None, sep='_'):
        tag = '' if (tag is None or not len(tag)) else sep+tag
        if not os.path.exists(folder):
            print(f' mkdir {folder}')
            os.makedirs(folder)
        file_name = os.path.join(folder, f'{self.name}{tag}.png')
        print(f' - saving {file_name}')
        plt.savefig(file_name, dpi=dpi, transparent=True)

class DataFile:
    def __init__(self, file_name, json_file=None):
        self.path, self.file = file_name, os.path.basename(file_name)
        self.json_file = f'{os.path.join(folder, name)}.json' if json_file is None else json_file
    def load_data(self):
        print(f'loading {self.path}')
        return np.loadtxt(self.path)
    def load_json(self):
        # print(f'loading {self.json_file}')
        with open(self.json_file, 'r') as f:
            config = json.load(f)
        return config
