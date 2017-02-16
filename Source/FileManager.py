import os
import xml.etree.ElementTree as ET
__author__ = 'Evan'


class XmlParser:
    def __init__(self, folder_name):
        # Initialize tree and root to None (uninitialized)
        self.tree = None
        self.root = None

        # If file exists, load it.
        if os.path.isfile(folder_name):
            self.tree = ET.parse(folder_name)
            self.root = self.tree.getroot()
        return

    def get_redditor_name_list(self):
        redditor_list = []
        if self.root is not None:
            for child in self.root.getchildren():
                redditor_list.append(child.attrib['name'])
        return redditor_list

    def get_redditor_keywords(self, redditor_name):
        keyword_list = []
        if self.root is not None:
            try:
                redditor = []
                keywords = []
                for child in self.root.getchilder():
                    if child.attrib['name'] == redditor_name:
                        redditor = child

                for child in redditor:
                    if child.tag == 'globalKeywords':
                        keywords = child

                for child in keywords:
                    keyword_list.append(child.attrib['name'])

            except:
                keyword_list = []

        return keyword_list

    def get_redditor_subreddits(self, redditor_name):
        subreddit_list = []
        if self.root is not None:
            try:
                redditor = []
                subreddits = []
                for child in self.root.getchilder():
                    if child.attrib['name'] == redditor_name:
                        redditor = child

                for child in redditor:
                    if child.tag == 'subreddits':
                        subreddits = child

                for child in subreddits:
                    subreddit_list.append(child.attrib['name'])

            except:
                subreddit_list = []

        return subreddit_list

    def get_redditor_times(self, redditor_name):
        times_list = []
        if self.root is not None:
            try:
                redditor = []
                times = []
                for child in self.root.getchilder():
                    if child.attrib['name'] == redditor_name:
                        redditor = child

                for child in redditor:
                    if child.tag == 'times':
                        times = child

                for child in times:
                    times_list.append(child.attrib['name'])

            except:
                times_list = []

        return times_list


def save_id_list(folder_name, id_list):
    with open(folder_name, "w") as f:
            for id_string in id_list:
                f.write(id_string + "\n")


def load_id_list(folder_name):
    if not os.path.isfile(folder_name):
        return list()
    else:
        with open(folder_name, "r") as f:
            redditors = f.read()
            redditors = redditors.split("\n")
            return list(filter(None, redditors))