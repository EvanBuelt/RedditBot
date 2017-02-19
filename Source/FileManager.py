import os
import xml.etree.ElementTree as ET
__author__ = 'Evan'


class XmlManager:
    def __init__(self, folder_name, save_file):
        # Initialize tree and root to None (uninitialized)
        self.tree = None
        self.root = None

        # Save folder name for saving
        self.folder_name = folder_name
        self.save_file = save_file

        # Identifiers for tags and attributes to make it easy to update/ensure reading and writing is consistent
        self.version_string = "version"
        self.redditor_name_string = "name"
        self.subreddits_string = "subreddits"
        self.global_keywords_string = "globalKeywords"
        self.times_string = "times"

        # Load the XML data
        self.load(folder_name)

    # Get version of saved data.
    def get_xml_version(self):
        major_version = 0
        minor_version = 0

        if self.root is not None:
            if self.version_string in self.root.keys():
                data = self.root.attrib[self.version_string]
                data = data.split('.')
                if len(data) == 0:
                    major_version = 0
                    minor_version = 0
                elif len(data) == 1:
                    major_version = data[0]
                elif len(data) == 2:
                    major_version, minor_version = data.split()
                else:
                    major_version = data[0]
                    minor_version = data[1]
        return major_version, minor_version

    # Returns a list of names in XML folder.  If no names are found, returns an empty list
    def get_redditor_name_list(self):
        redditor_list = []
        if self.root is not None:
            for child in self.root.getchildren():
                # TODO: create and use variables for tag and attribute names
                redditor_list.append(child.attrib['name'])
        return redditor_list

    # Returns a list of global keywords for the redditor.  Returns empty list if none found
    def get_redditor_keywords(self, redditor_name):
        keyword_list = []
        if self.root is not None:
            redditor = self.get_redditor_child(redditor_name)
            keywords = self.get_tag(redditor, self.global_keywords_string)

            for child in keywords:
                # TODO: create and use variables for tag and attribute names
                keyword_list.append(child.attrib['name'])

        return keyword_list

    # Gets list of subreddits for the redditor.  Returns empty list if none found
    def get_redditor_subreddits(self, redditor_name):
        subreddit_list = []
        if self.root is not None:
            # TODO: check if tag is in data. If not found, figure out what to do
            redditor = self.get_redditor_child(redditor_name)
            subreddits = self.get_tag(redditor, self.subreddits_string)

            for child in subreddits:
                # TODO: create and use variables for tag and attribute names
                subreddit_list.append(child.attrib['name'])

        return subreddit_list

    # Gets list of times for the redditor.  Returns empty list if none found
    def get_redditor_times(self, redditor_name):
        times_list = []
        if self.root is not None:
            # TODO: check if tag is in data. If not found, figure out what to do
            redditor = self.get_redditor_child(redditor_name)
            times = self.get_tag(redditor, self.times_string)

            for child in times:
                # TODO: create and use variables for tag and attribute names
                times_list.append(child.attrib['name'])

        return times_list

    # Adds a new redditor to xml data. Sets up required elements in redditor. Returns true if setup and false otherwise
    def add_redditor(self, redditor_name):
        if self.root is not None:

            # Don't add redditor if the redditor already exists
            if redditor_name in self.get_redditor_name_list():
                return False
            else:
                # Create version string
                major_version, minor_version = self.get_xml_version()
                version_str = str(major_version) + '.' + str(minor_version)

                # TODO: create and use variables for tag and attribute names
                # Create xml elements for redditor
                redditor = ET.Element('redditor', {'name': redditor_name, 'version': version_str})
                subreddits = ET.Element(self.subreddits_string)
                keywords = ET.Element(self.global_keywords_string)
                times = ET.Element(self.times_string)

                # Setup xml for redditor
                self.root.append(redditor)
                redditor.append(subreddits)
                redditor.append(keywords)
                redditor.append(times)
            return True
        return False

    # Adds list of subreddits to xml. Returns list of subreddits added
    def add_subreddits(self, redditor_name, subreddits):
        redditor_object = self.get_redditor_child(redditor_name)
        # TODO: create and use variables for tag and attribute names
        subreddit_object = self.get_tag(redditor_object, self.subreddits_string)

        # TODO: get list of subreddits already in the xml first to avoid adding duplicates
        current_subreddits = self.get_redditor_subreddits(redditor_name)
        new_subreddits = []

        for subreddit in subreddits:
            if subreddit not in current_subreddits:
                new_subreddits.append(subreddit)

        for subreddit in new_subreddits:
            # TODO: create and use variables for tag and attribute names
            subreddit_element = ET.Element('subreddit', {'name': subreddit})
            subreddit_object.append(subreddit_element)
        return

    # Adds list of global keywords to xml. Returns list of keywords added
    def add_keywords(self, redditor_name, keywords):
        redditor_object = self.get_redditor_child(redditor_name)
        keyword_object = self.get_tag(redditor_object, self.global_keywords_string)

        # TODO: get list of keywords already in the xml first to avoid adding duplicates
        current_keywords = self.get_redditor_keywords(redditor_name)
        new_keywords = []

        for keyword in keywords:
            if keyword not in current_keywords:
                new_keywords.append(keyword)

        for keyword in new_keywords:
            # TODO: create and use variables for tag and attribute names
            keyword_element = ET.Element('keyword', {'name': keyword})
            keyword_object.append(keyword_element)
        return

    # Adds list of times to xml. Returns list of times added
    def add_times(self, redditor_name, times):
        redditor_object = self.get_redditor_child(redditor_name)
        # TODO: create and use variables for tag and attribute names
        time_object = self.get_tag(redditor_object, self.times_string)

        # TODO: get list of times already in the xml first to avoid adding duplicates
        current_times = self.get_redditor_times(redditor_name)
        new_times = []

        for time in times:
            if time not in current_times:
                new_times.append(time)

        for time in new_times:
            # TODO: create and use variables for tag and attribute names
            time_element = ET.Element('time', {'name': time})
            time_object.append(time_element)
        return

    def get_redditor_child(self, redditor_name):
        redditor_object = []
        for child in self.root.getchildren():
            # TODO: create and use variables for tag and attribute names
            if child.attrib['name'] == redditor_name:
                redditor_object = child

        return redditor_object

    def get_tag(self, xml_object, tag_name):
        tag_object = []
        for child in xml_object.getchildren():
            # TODO: check if tag exists (may not be needed here)
            if child.tag == tag_name:
                tag_object = child

        return tag_object

    # TODO: Create different load functions for different versions
    # Loading and saving of the xml.
    def load(self, folder_name):
        # If file exists, load it.
        if os.path.isfile(folder_name):
            self.tree = ET.parse(folder_name)
            self.root = self.tree.getroot()
        else:
            self.root = ET.Element('data')
            self.tree = ET.ElementTree(self.root)
        return

    # Save the xml data. Only one save is likely needed as the xml should be saved to latest version
    def save(self):
        # TODO: Maybe add a variable to save major/minor version as well
        self.tree.write(self.save_file)


# Save a list of IDs. Used for message IDs (as they are constant) and redditors (form of IDs)
def save_id_list(folder_name, id_list):
    with open(folder_name, "w") as f:
            for id_string in id_list:
                f.write(id_string + "\n")


# Load a list of IDs. Used for message IDs (as they are constant) and redditors (form of IDs)
def load_id_list(folder_name):
    if not os.path.isfile(folder_name):
        return list()
    else:
        with open(folder_name, "r") as f:
            redditors = f.read()
            redditors = redditors.split("\n")
            return list(filter(None, redditors))