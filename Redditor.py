import os
__author__ = 'Evan'


class AccountManager:
    def __init__(self, reddit, name, subscribed):
        # Set name of redditter associated with class
        self.name = name

        # Get a redditor object to message redditor
        self.redditor = reddit.redditor(name)

        # Keep track of whether the user is subscribed
        self.subscribed = subscribed

        # Get folder name of posts previously sent to particular redditter
        # along with subreddits associated with redditter
        self.id_folder_name = name + "_id.txt"
        self.subreddit_folder_name = name + "_sr.txt"
        self.keyword_folder_name = name + "_kw.txt"

        # Open list of IDs sent to redditor. If no file exists, create it
        if not os.path.isfile(self.id_folder_name):
            self.post_list = []
        else:
            with open(self.id_folder_name, "r") as f:
                posts = f.read()
                posts = posts.split("\n")
                self.post_list = list(filter(None, posts))

        # Open list of subreddits redditor is subscribed. If no file exists, create it
        if not os.path.isfile(self.subreddit_folder_name):
            self.subreddit_list = []
        else:
            with open(self.subreddit_folder_name, "r") as f:
                subreddits = f.read()
                subreddits = subreddits.split("\n")
                self.subreddit_list = list(filter(None, subreddits))

        # Open list of subreddits redditor is subscribed.If no file exists, create it
        if not os.path.isfile(self.keyword_folder_name):
            self.keyword_list = []
        else:
            with open(self.keyword_folder_name, "r") as f:
                keywords = f.read()
                keywords = keywords.split("\n")
                self.keyword_list = list(filter(None, keywords))
        return

    # Functionality to add/remove subreddits
    def add_subreddit(self, subreddit_name):
        if subreddit_name not in self.subreddit_list:
            self.subreddit_list.append(subreddit_name)
            self.save()
        return

    def remove_subreddit(self, subreddit_name):
        if subreddit_name in self.subreddit_list:
            self.subreddit_list.remove(subreddit_name)
            self.save()
        return

    # Functionality to add/remove keywords
    def add_keyword(self, keyword_name):
        if keyword_name not in self.keyword_list:
            self.keyword_list.append(keyword_name)
            self.save()
        return

    def remove_keyword(self, keyword_name):
        if keyword_name in self.keyword_list:
            self.keyword_list.remove(keyword_name)
            self.save()
        return

    # Get posts from subreddits and send them if keyword is found
    def process_posts(self, reddit, limit_per_subreddit):
        if self.subscribed:
            for subreddit_name in self.subreddit_list:
                self.send_posts(reddit, subreddit_name, limit_per_subreddit)
        return

    def send_posts(self, reddit, subreddit_name, limit_per_subreddit):
        subreddit = reddit.subreddit(subreddit_name)
        title = "New posts from " + subreddit_name
        message = ""
        i = 1
        for submission in subreddit.new(limit=limit_per_subreddit):
            # Only look at ids not already found
            if submission.id not in self.post_list:
                self.post_list.append(submission.id)

                # Iterate over all keywords to see if they are found in the title
                for keyword in self.keyword_list:
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

    # Save list of IDs and subreddits appropriately
    def save(self):
        with open(self.id_folder_name, "w") as f:
            for post_id in self.post_list:
                f.write(post_id + "\n")

        with open(self.subreddit_folder_name, "w") as f:
            for subreddit in self.subreddit_list:
                f.write(subreddit + "\n")

        with open(self.keyword_folder_name, "w") as f:
            for keyword in self.keyword_list:
                f.write(keyword + "\n")
        return


class Message:
    def __init__(self):
        return
