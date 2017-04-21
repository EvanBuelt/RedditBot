import Source.ExceptionHandler
import FileManager

__author__ = 'Evan'


class AccountManager:
    def __init__(self, reddit, name, xml_manager, subscribed):
        # Set name of redditter associated with class
        self.name = name

        # Get a redditor object to message redditor
        self.redditor = reddit.redditor(name)

        # Keep track of whether the user is subscribed
        self.subscribed = subscribed

        # Get folder name of posts previously sent to particular redditter
        self.id_folder_name = "data/" + name + "_id.txt"
        self.xml_manager = xml_manager

        # List of ids of subreddits, subreddits, and keywords
        self.post_list = []

        # Version number of redditor
        self.version = ""

        self.load_version_0_1()
        return

    # Functionality to add/remove/get subreddits
    def add_subreddit(self, subreddit_name):
        return self.xml_manager.add_subreddits(self.name, [subreddit_name])

    def remove_subreddit(self, subreddit_name):
        return self.xml_manager.remove_subreddits(self.name, [subreddit_name])

    def get_subreddit_name_list(self):
        return self.xml_manager.get_subreddits(self.name)

    # Functionality to add/remove/get global keywords
    def add_global_keyword(self, keyword_name):
        return self.xml_manager.add_global_keywords(self.name, [keyword_name])

    def remove_global_keyword(self, keyword_name):
        return self.xml_manager.remove_global_keywords(self.name, [keyword_name])

    def get_global_keyword_list(self):
        return self.xml_manager.get_global_keywords(self.name)

    # Functionality to add/remove/get keywords in subreddits
    def add_subreddit_keyword(self, keyword_name, subreddit_name):
        return self.xml_manager.add_subreddit_keywords(self.name, subreddit_name, [keyword_name])

    def remove_subreddit_keyword(self, keyword_name, subreddit_name):
        return self.xml_manager.remove_subreddit_keywords(self.name, subreddit_name, [keyword_name])

    def get_subreddit_keyword_list(self, subreddit_name):
        return self.xml_manager.get_subreddit_keywords(self.name, subreddit_name)

    # Functionality to add/remove/get times
    def add_time(self, new_time):
        return self.xml_manager.add_times(self.name, [new_time])

    def remove_time(self, old_time):
        return self.xml_manager.remove_times(self.name, [old_time])

    def get_time_list(self):
        return self.xml_manager.get_times(self.name)

    # Get posts from subreddits and send them if keyword is found
    def process_posts(self, reddit, limit_per_subreddit):
        if self.subscribed:
            for subreddit in self.get_subreddit_name_list():
                Source.ExceptionHandler.praw_caller(self.send_posts, "Exception handled in getting subreddits", reddit, subreddit, limit_per_subreddit)
        return

    def send_posts(self, reddit, subreddit_name, limit_per_subreddit):

        subreddit = reddit.subreddit(subreddit_name)
        title = "New posts from " + subreddit_name
        message = ""
        link_num = 1

        for submission in subreddit.new(limit=limit_per_subreddit):
            if link_num <= 15:
                # Only look at ids not already found
                if submission.id not in self.post_list:
                    self.post_list.append(submission.id)

                    combined_keywords = []

                    for keyword in self.get_global_keyword_list():
                        if keyword.lower() not in combined_keywords:
                            combined_keywords.append(keyword.lower())

                    for keyword in self.get_subreddit_keyword_list(subreddit_name):
                        if keyword.lower() not in combined_keywords:
                            combined_keywords.append(keyword.lower())

                    # Iterate over all keywords to see if they are found in the title
                    for keyword in combined_keywords:
                        if keyword.lower() in submission.title.lower():
                            message = message + str(link_num) + ". [" + submission.title + "](" + \
                                      submission.permalink + ")  \n\n"
                            link_num += 1
                            break

        # If there was something found, send a message to the redditor
        if message is not "":
            self.message(title, message)
            print "Sent message to " + self.name

    # Abstraction to send a message
    def message(self, title, message):
        Source.ExceptionHandler.praw_caller(self.redditor.message, "Exception handled in sending a message", title, message)

    # Load list of IDs, subreddits, and keywords appropriately
    def load_version_0_1(self):
        self.post_list = FileManager.load_id_list(self.id_folder_name)

        self.subscribed = self.xml_manager.get_subscribed(self.name)

        print self.name
        print self.xml_manager.get_global_keywords(self.name)
        print self.xml_manager.get_times(self.name)
        print self.subscribed
        print "Subreddits: "
        for subreddit_name in self.get_subreddit_name_list():
            print subreddit_name, self.get_subreddit_keyword_list(subreddit_name)
        print ""

    # Save list of IDs, subreddits, and keywords appropriately
    def save_version_0_1(self):
        try:
            # Save list of submission ids
            FileManager.save_id_list(self.id_folder_name, self.post_list)

            # Set Version Number of redditor format
            self.xml_manager.set_redditor_xml_version(self.name, 0, 1)

            # Save whether user is subscribed
            self.xml_manager.set_subscribed(self.name, self.subscribed)

            self.xml_manager.save()
        except:
            print "Failed to save data for " + self.name

        return
