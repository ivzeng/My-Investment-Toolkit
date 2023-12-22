import json
import os.path as osp


class MyJson:

    def __init__(self) -> None:
        pass

    def load(self, json_file_dir: str, default: dict = dict()) -> dict:
        '''
        Loads JSON file to a dict and returns
        Creates an default file if such file does not exits
        '''
        if not osp.exists(json_file_dir):
            self.write(json_file_dir, default)
        with open(json_file_dir, 'r') as config_file:
            return json.loads(config_file.read())
    
    def write(self, json_file_dir: str, contents: dict) -> None:
        '''
        Writes json file
        '''
        with open(json_file_dir, 'w') as config_file:
            config_file.write(json.dumps(contents, indent=4))



