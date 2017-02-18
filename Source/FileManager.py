import os
import xml.etree.ElementTree as ET
__author__ = 'Evan'


class XmlParser:
    def __init__(self, folder_name, save_file):
        # Initialize tree and root to None (uninitialized)
        self.tree = None
        self.root = None

        # Save folder name for saving
        self.folder_name = folder_name
        self.save_file = save_file

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
                redditor = self.get_redditor_child(redditor_name)
                keywords = self.get_tag(redditor, 'globalKeywords')

                for child in keywords:
                    keyword_list.append(child.attrib['name'])

            except:
                keyword_list = []

        return keyword_list

    def get_redditor_subreddits(self, redditor_name):
        subreddit_list = []
        if self.root is not None:
            try:
                redditor = self.get_redditor_child(redditor_name)
                subreddits = self.get_tag(redditor, 'subreddits')

                for child in subreddits:
                    subreddit_list.append(child.attrib['name'])

            except:
                subreddit_list = []

        return subreddit_list

    def get_redditor_times(self, redditor_name):
        times_list = []
        if self.root is not None:
            try:
                redditor = self.get_redditor_child(redditor_name)
                times = self.get_tag(redditor, 'times')

                for child in times:
                    times_list.append(child.attrib['name'])

            except:
                times_list = []

        return times_list

    def add_redditor(self, redditor_name):
        if self.root is not None:

            for name in self.get_redditor_name_list():
                if name == redditor_name:
                    return

            redditor = ET.Element('redditor', {'name' : redditor_name})
            subreddits = ET.Element('subreddits')
            keywords = ET.Element('globalKeywords')
            times = ET.Element('times')

            self.root.append(redditor)
            redditor.append(subreddits)
            redditor.append(keywords)
            redditor.append(times)
        return

    def add_subreddits(self, redditor_name, subreddits):
        redditor_object = self.get_redditor_child(redditor_name)
        subreddit_object = self.get_tag(redditor_object, 'subreddits')

        for subreddit in subreddits:
            subreddit_element = ET.Element('subreddit', {'name': subreddit})
            subreddit_object.append(subreddit_element)
        return

    def add_keywords(self, redditor_name, keywords):
        redditor_object = self.get_redditor_child(redditor_name)
        keyword_object = self.get_tag(redditor_object, 'keywords')

        for subreddit in keywords:
            subreddit_element = ET.Element('keyword', {'name': subreddit})
            keyword_object.append(subreddit_element)
        return

    def add_times(self, redditor_name, times):
        redditor_object = self.get_redditor_child(redditor_name)
        time_object = self.get_tag(redditor_object, 'times')

        for subreddit in times:
            subreddit_element = ET.Element('time', {'name': subreddit})
            time_object.append(subreddit_element)
        return

    def get_redditor_child(self, redditor_name):
        redditor_object = []
        for child in self.root.getchildren():
            if child.attrib['name'] == redditor_name:
                redditor_object = child

        return redditor_object

    def get_tag(self, xml_object, tag_name):
        tag_object = []
        for child in xml_object.getchildren():
            if child.tag == tag_name:
                tag_object = child

        return tag_object

    def save(self):
        self.tree.write(self.save_file)


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