import json
import collections
import os

class Settings():
    def save(self):
        with open(self.file_path, 'w') as settings_file:
            json.dump(self.data, settings_file, indent=4)

    def __init__(self, file_path):
        with open(file_path) as settings_file:
            self.file_path = file_path
            self.data = json.load(settings_file, object_pairs_hook=collections.OrderedDict)
