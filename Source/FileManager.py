import os
import xml.etree.ElementTree as ET
__author__ = 'Evan'


class XmlLoader:
    def __init__(self, load_folder_name, save_folder_name=None):
        # Initialize tree and root to None (uninitialized)
        self.tree = None
        self.root = None

        # If no save folder is given, then any data saved will be in where the data was loaded
        if save_folder_name is None:
            self.save_folder_name = load_folder_name
        else:
            self.save_folder_name = save_folder_name

        # String used to load overall version of data
        self.version_string = "version"

        # Load data
        self.load(load_folder_name)

    # Gets root for use in XML Manager
    def get_root(self):
        return self.root

    # Gets version of overall data.
    def get_xml_version(self):
        # Major/Minor version of 0.0 means no version was found
        major_version = 0
        minor_version = 0

        # If data was loaded, root will not be None
        if self.root is not None:
            # Only get the version if the version string is found as a base attribute
            if self.version_string in self.root.keys():
                data = self.root.attrib[self.version_string]
                data = data.split('.')

                # No data means it wasn't found
                if len(data) == 0:
                    major_version = 0
                    minor_version = 0

                # Data length of 1 means there is no minor version
                elif len(data) == 1:
                    major_version = data[0]

                # Data length of 2 means there is a major and minor version available
                elif len(data) == 2:
                    major_version, minor_version = data.split()

                # If more than two versions are found, the data is likely in a future format
                else:
                    major_version = data[0]
                    minor_version = data[1]

        # Returning a version of (0, 0) implies no version data was found.
        return major_version, minor_version

    # Load the xml data.
    def load(self, folder_name):
        # If file exists, load it.
        if os.path.isfile(folder_name):
            self.tree = ET.parse(folder_name)
            self.root = self.tree.getroot()
        else:
            self.root = ET.Element('data')
            self.tree = ET.ElementTree(self.root)
        return

    # Save the xml data.
    def save(self):
        # TODO: Maybe add a variable to save major/minor version as well
        self.tree.write(self.save_folder_name)


class XmlManager:
    def __init__(self, xml_loader):
        # Save Xml Loader for future reference
        self.xml_loader = xml_loader

        # Initialize root to None (uninitialized)
        self.root = self.xml_loader.get_root()

        # Identifiers for tags and attributes to make it easy to update/ensure reading and writing is consistent
        self.name_string = "name"
        self.redditor_version_string = "version"
        self.subreddits_string = "subreddits"
        self.subreddit_keywords_string = "subredditKeywords"
        self.global_keywords_string = "globalKeywords"
        self.times_string = "times"

    # Get version of saved data.
    def get_xml_version(self):
        return self.xml_loader.get_xml_version()

    '''
    Section for adding, removing, and getting global keywords
    '''

    # Returns a list of global keywords for the redditor.  Returns empty list if no keywords were found
    def get_redditor_keywords(self, redditor_name):
        keyword_list = []
        if self.root is not None:
            redditor = self.get_redditor_child(redditor_name)
            keywords = self.get_tag(redditor, self.global_keywords_string)

            for child in keywords:
                keyword_list.append(child.attrib[self.name_string])

        return keyword_list

    # Adds list of global keywords to xml. Returns list of keywords added
    def add_keywords(self, redditor_name, keywords):
        redditor_object = self.get_redditor_child(redditor_name)
        keyword_object = self.get_tag(redditor_object, self.global_keywords_string)

        current_keywords = self.get_redditor_keywords(redditor_name)
        new_keywords = []

        for keyword in keywords:
            if keyword not in current_keywords:
                new_keywords.append(keyword)

        for keyword in new_keywords:
            # TODO: create and use variables for tag and attribute names
            keyword_element = ET.Element('keyword', {self.name_string: keyword})
            keyword_object.append(keyword_element)
        return

    def remove_keywords(self, redditor_name, keywords):
        redditor_object = self.get_redditor_child(redditor_name)
        keyword_object = self.get_tag(redditor_object, self.global_keywords_string)

        keyword_elements_removal = []

        # Find all keywords in list provided in xml data object
        for keyword_element in keyword_object:
            if keyword_element.attrib[self.name_string] in keywords:
                keyword_elements_removal.append(keyword_element)

        # Remove all found keywords from xml data
        for keyword_element in keyword_elements_removal:
            keyword_object.remove(keyword_element)
        return

    '''
    Section for adding, removing, and getting subreddits
    '''

    # Gets list of subreddits for the redditor.  Returns empty list if none found
    def get_redditor_subreddits(self, redditor_name):
        subreddit_list = []
        if self.root is not None:
            # TODO: check if tag is in data. If not found, figure out what to do
            redditor = self.get_redditor_child(redditor_name)
            subreddits = self.get_tag(redditor, self.subreddits_string)

            for child in subreddits:
                subreddit_list.append(child.attrib[self.name_string])

        return subreddit_list

    # Adds list of subreddits to xml. Returns list of subreddits added
    def add_subreddits(self, redditor_name, subreddits):
        redditor_object = self.get_redditor_child(redditor_name)
        subreddit_object = self.get_tag(redditor_object, self.subreddits_string)

        current_subreddits = self.get_redditor_subreddits(redditor_name)
        new_subreddits = []

        for subreddit in subreddits:
            if subreddit not in current_subreddits:
                new_subreddits.append(subreddit)

        for subreddit in new_subreddits:
            # TODO: create and use variables for tag and attribute names
            subreddit_element = ET.Element('subreddit', {self.name_string: subreddit})
            subreddit_object.append(subreddit_element)
        return

    def remove_subreddits(self, redditor_name, subreddits):
        redditor_object = self.get_redditor_child(redditor_name)
        subreddit_object = self.get_tag(redditor_object, self.subreddits_string)

        subreddit_elements_removal = []

        # Find all keywords in list provided in xml data object
        for subreddit_element in subreddit_object:
            if subreddit_element.attrib[self.name_string] in subreddits:
                subreddit_elements_removal.append(subreddit_element)

        # Remove all found keywords from xml data
        for subreddit_element in subreddit_elements_removal:
            subreddit_object.remove(subreddit_element)
        return

    '''
    Section for adding, removing, and getting times
    '''

    # Gets list of times for the redditor.  Returns empty list if none found
    def get_redditor_times(self, redditor_name):
        times_list = []
        if self.root is not None:
            redditor = self.get_redditor_child(redditor_name)
            times = self.get_tag(redditor, self.times_string)

            for child in times:
                # TODO: create and use variables for tag and attribute names
                times_list.append(child.attrib[self.name_string])

        return times_list

    # Adds list of times to xml. Returns list of times added
    def add_times(self, redditor_name, times):
        redditor_object = self.get_redditor_child(redditor_name)
        time_object = self.get_tag(redditor_object, self.times_string)

        current_times = self.get_redditor_times(redditor_name)
        new_times = []

        for time in times:
            if time not in current_times:
                new_times.append(time)

        for time in new_times:
            # TODO: create and use variables for tag and attribute names
            time_element = ET.Element('time', {self.name_string: time})
            time_object.append(time_element)
        return

    def remove_times(self, redditor_name, times):
        redditor_object = self.get_redditor_child(redditor_name)
        time_object = self.get_tag(redditor_object, self.times_string)

        subreddit_elements_removal = []

        # Find all keywords in list provided in xml data object
        for time_element in time_object:
            if time_element.attrib[self.name_string] in times:
                subreddit_elements_removal.append(time_element)

        # Remove all found keywords from xml data
        for time_element in subreddit_elements_removal:
            time_object.remove(time_element)
        return

    '''
    Support for adding, removing, and getting redditors, along with getting a list of redditor names and xml version
    '''

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
                redditor = ET.Element('redditor', {self.name_string: redditor_name, self.redditor_version_string: version_str})
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

    # Get version of redditor's data.  As data is only updated on change, the structure of the data may be different,
    # so this is useful when updating from old versions of data
    def get_redditor_xml_version(self):
        return 0, 0

    # Returns a list of names in XML folder.  If no names are found, returns an empty list
    def get_redditor_name_list(self):
        redditor_list = []
        if self.root is not None:
            for child in self.root.getchildren():
                redditor_list.append(child.attrib[self.name_string])
        return redditor_list

    '''
    Internal support for functions
    '''
    def get_redditor_child(self, redditor_name):
        redditor_object = []
        for child in self.root.getchildren():
            if child.attrib[self.name_string] == redditor_name:
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
        self.xml_loader.load(folder_name)
        self.root = self.xml_loader.get_root()

    # Save the xml data. Only one save is likely needed as the xml should be saved to latest version
    def save(self):
        # TODO: Maybe add a variable to save major/minor version as well
        self.xml_loader.save()


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