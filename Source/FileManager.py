import os
__author__ = 'Evan'


def save_id_list(folder_name, id_list):
    if os.path.isfile(folder_name):
        with open(folder_name, "w") as f:
                for id_string in id_list:
                    f.write(id_string + "\n")
    else:
        raise IOError("Invalid folder path")


def load_id_list(folder_name):
    if not os.path.isfile(folder_name):
        return list()
    else:
        with open(folder_name, "r") as f:
            redditors = f.read()
            redditors = redditors.split("\n")
            return list(filter(None, redditors))