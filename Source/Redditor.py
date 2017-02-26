import FileManager

__author__ = 'Evan'


class Subreddit:
    def __init__(self, name):
        self.name = name
        self.keyword_list = []
        return

    def add_keyword(self, keyword):
        if keyword not in self.keyword_list:
            self.keyword_list.append(keyword)
            return True
        return False

    def remove_keyword(self, keyword):
        if keyword in self.keyword_list:
            self.keyword_list.remove(keyword)
            return True
        return False


class AccountManager:
    def __init__(self, reddit, name, xml_manager):
        # Set name of redditter associated with class
        self.name = name

        # Get a redditor object to message redditor
        self.redditor = reddit.redditor(name)

        # Keep track of whether the user is subscribed
        self.subscribed = False

        # Get folder name of posts previously sent to particular redditter
        self.id_folder_name = name + "_id.txt"
        self.xml_manager = xml_manager

        # List of ids of subreddits, subreddits, and keywords
        self.post_list = []
        self.subreddit_list = []
        self.keyword_list = []

        # Version number of redditor
        self.version = ""

        self.load_version_0_1()
        return

    # Functionality to add/remove/get subreddits
    def add_subreddit(self, subreddit_name):
        found = False
        for subreddit in self.subreddit_list:
            if subreddit.name == subreddit_name:
                found = True

        if not found:
            self.subreddit_list.append(Subreddit(subreddit_name))
            return True
        return False

    def remove_subreddit(self, subreddit_name):
        subreddit_to_remove = None
        for subreddit in self.subreddit_list:
            if subreddit.name == subreddit_name:
                subreddit_to_remove = subreddit

        if subreddit_to_remove is not None:
            self.subreddit_list.remove(subreddit_to_remove)
            return True
        return False

    def get_subreddit_name_list(self):
        name_list = []
        for subreddit in self.subreddit_list:
            name_list.append(subreddit.name)
        return name_list

    # Functionality to add/remove/get global keywords
    def add_global_keyword(self, keyword_name):
        if keyword_name not in self.keyword_list:
            self.keyword_list.append(keyword_name)
            return True
        return False

    def remove_global_keyword(self, keyword_name):
        if keyword_name in self.keyword_list:
            self.keyword_list.remove(keyword_name)
            return True
        return False

    def get_global_keyword_list(self):
        keyword_list = []
        for keyword_name in self.keyword_list:
            keyword_list.append(keyword_name)
        return keyword_list

    # Functionality to add/remove/get keywords in subreddits
    def add_subreddit_keyword(self, keyword_name, subreddit_name):
        for subreddit in self.subreddit_list:
            if subreddit.name == subreddit_name:
                return subreddit.add_keyword(keyword_name)
        return False

    def remove_subreddit_keyword(self, keyword_name, subreddit_name):
        for subreddit in self.subreddit_list:
            if subreddit.name == subreddit_name:
                return subreddit.remove_keyword(keyword_name)
        return False

    def get_subreddit_keyword_list(self, subreddit_name):
        keyword_list = []
        for subreddit in self.subreddit_list:
            if subreddit.name == subreddit_name:
                for keyword in subreddit.keyword_list:
                    keyword_list.append(keyword)
        return keyword_list
    
    # Get posts from subreddits and send them if keyword is found
    def process_posts(self, reddit, limit_per_subreddit):
        if self.subscribed:
            for subreddit in self.subreddit_list:
                self.send_posts(reddit, subreddit, limit_per_subreddit)
        return

    def send_posts(self, reddit, subreddit_object, limit_per_subreddit):
        subreddit = reddit.subreddit(subreddit_object.name)
        title = "New posts from " + subreddit_object.name
        message = ""
        i = 1
        for submission in subreddit.new(limit=limit_per_subreddit):
            # Only look at ids not already found
            if submission.id not in self.post_list:
                self.post_list.append(submission.id)

                combined_keywords = [keyword for keyword in self.keyword_list]
                for keyword in subreddit_object.keyword_list:
                    if keyword not in combined_keywords:
                        combined_keywords.append(keyword)

                # Iterate over all keywords to see if they are found in the title
                for keyword in combined_keywords:
                    if keyword in submission.title:
                        message = message + str(i) + ". [" + submission.title + "](" + submission.permalink + ").  "
                        i += 1
                        break

        # If there was something found, send a message to the redditor
        if message is not "":
            self.redditor.message(title, message)
        return

    # Abstraction to send a message
    def message(self, title, message):
        self.redditor.message(title, message)
        return

    # Load list of IDs, subreddits, and keywords appropriately
    def load_version_0_1(self):
        self.post_list = FileManager.load_id_list(self.id_folder_name)

        self.subreddit_list = []
        for subreddit_name in self.xml_manager.get_subreddits(self.name):
            self.subreddit_list.append(Subreddit(subreddit_name))

        self.keyword_list = self.xml_manager.get_global_keywords(self.name)
        self.subscribed = self.xml_manager.get_subscribed(self.name)

        print self.name
        print self.subreddit_list
        print self.keyword_list
        print self.subscribed

    # Save list of IDs, subreddits, and keywords appropriately
    def save_version_0_1(self):
        try:
            # Save list of submission ids
            FileManager.save_id_list(self.id_folder_name, self.post_list)

            # Set Version Number of redditor format
            self.xml_manager.set_redditor_xml_version(self.name, 0, 1)

            # Save subreddits and subreddit keywords
            subreddit_name_list = []

            for subreddit_object in self.subreddit_list:
                # Append name of subreddit to list
                subreddit_name_list.append(subreddit_object.name)

            # Save list of subreddits
            self.xml_manager.clear_subreddits(self.name)
            self.xml_manager.add_subreddits(self.name, subreddit_name_list)

            # Save list of subreddit keywords
            for subreddit_object in self.subreddit_list:
                # Syntactic sugar
                name = subreddit_object.name
                keyword_list = subreddit_object.keyword_list

                # Clear subreddit keywords and add current keywords (in case a few were deleted)
                self.xml_manager.clear_subreddit_keywords(self.name, name)
                self.xml_manager.add_subreddit_keywords(self.name, name, keyword_list)

            # Save global keywords
            self.xml_manager.clear_global_keywords(self.name)
            self.xml_manager.add_global_keywords(self.name, self.keyword_list)

            # Save whether user is subscribed
            self.xml_manager.set_subscribed(self.name, self.subscribed)

            self.xml_manager.save()
        except:
            print "Failed to save data for " + self.name

        return
