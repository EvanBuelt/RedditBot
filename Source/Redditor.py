import os
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


class MessageManager:
    def __init__(self):
        # Commands used for help
        self.command_menu = [("Subscribe", "Subscribes to the bot.  If you had a list of keywords and subreddits, these will be retained"),
                             ("Unsubscribe", "Unsubscribes from the bot.  This will keep your list of keywords and subreddits"),
                             ("Clear", "Clears list of subreddits and keywords"),
                             ("Add Subreddit", "Adds a single subreddit this bot will check."),
                             ("Remove Subreddit", "Removes a single subreddit from your list of subreddits this bot checks."),
                             ("Get Subreddit", "Gets list of subreddits.  Same as 'Get Subreddits' command"),
                             ("Add Subreddits", "Adds multiple subreddits this bot will check."),
                             ("Remove Subreddits", "Removes multiple subreddits from your list of subreddits this bot checks."),
                             ("Get Subreddits", "Gets list of subreddits.  Same as 'Get Subreddit' command"),
                             ("Add Keyword", "Adds a single keyword to check in the list of subreddits."),
                             ("Remove Keyword", "Removes a single keyword from your list of keywords."),
                             ("Get Keyword", "Gets list of keywords.  Same as 'Get Keywords' command"),
                             ("Add Keywords", "Adds multiple keywords to check in the list of subreddits."),
                             ("Remove Keywords", "Removes multiple keywords from your list of keywords."),
                             ("Get Keywords", "Gets list of keywords.  Same as 'Get Keyword' command")]

        return

    def process_message(self, message, redditter_object):

        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        # There are a few one word instructions, so process these
        if len(words) == 1:
            instruction = words[0]

            if instruction.lower() == "help":
                self.process_help(message, redditter_object, None)
            elif instruction.lower() == "unsubscribe":
                self.process_subscribe(message, redditter_object)
            elif instruction.lower() == "subscribe":
                self.process_unsubscribe(message, redditter_object)
            elif instruction.lower() == "clear":
                self.process_clear(message, redditter_object)
            else:
                self.process_unknown(message, redditter_object)

        # These are two word instructions.
        elif len(words) >= 2:
            instruction = words[0]

            if instruction.lower() == "help":
                command = words[1]
                if len(words) >= 3:
                    command = command + " " + words[2]

                self.process_help(message, redditter_object, command)
            elif instruction.lower() == "get":
                second_instruction = words[1]

                if second_instruction.lower() == "subreddit":
                    self.process_get_subreddits(message, redditter_object)
                elif second_instruction.lower() == "subreddits":
                    self.process_get_subreddits(message, redditter_object)
                elif second_instruction.lower() == "keyword":
                    self.process_get_keyword(message, redditter_object)
                elif second_instruction.lower() == "keywords":
                    self.process_get_keyword(message, redditter_object)
                else:
                    self.process_unknown(message, redditter_object)

            elif instruction.lower() == "add":
                print "First instruction is add"
                # If the instruction is add, then the next instruction is either subreddit or keyword
                if len(words) >= 3:
                    second_instruction = words[1]

                    if second_instruction.lower() == "subreddit":
                        self.process_add_subreddit(message, redditter_object)
                    elif second_instruction.lower() == "subreddits":
                        self.process_add_subreddit(message, redditter_object)
                    elif second_instruction.lower() == "keyword":
                        self.process_add_keyword(message, redditter_object)
                    elif second_instruction.ower() == "keywords":
                        self.process_add_keyword(message, redditter_object)
                    else:
                        self.process_unknown(message, redditter_object)

            elif instruction.lower() == "remove":
                print "First instruction is remove"
                # If the instruction is add, then the next instruction is either subreddit or keyword
                if len(words) >= 3:
                    second_instruction = words[1]

                    if second_instruction.lower() == "subreddit":
                        self.process_remove_subreddit(message, redditter_object)
                    elif second_instruction.lower() == "subreddits":
                        self.process_remove_subreddit(message, redditter_object)
                    elif second_instruction.lower() == "keyword":
                        self.process_remove_keyword(message, redditter_object)
                    elif second_instruction.ower() == "keywords":
                        self.process_remove_keyword(message, redditter_object)
                    else:
                        self.process_unknown(message, redditter_object)
            else:
                self.process_unknown(message, redditter_object)

    def process_help(self, message, redditter_object, command):
        if command is None:
            reply = "Here are the commands I accept: "
            for item in self.command_menu:
                (menu, help_text) = item

                reply = reply + menu + ", "

            message.reply(reply)
        else:
            for item in self.command_menu:
                (menu, help_text) = item
                if command.lower() == menu.lower():
                    message.reply(command + ": " + help_text)

        return

    def process_get_subreddits(self, message, redditter_object):
        print "Getting subreddits"
        # Get body of message and split into words

        reply_message = "Your subreddits: "
        first = True

        for subreddit_object in redditter_object.subreddit_list:
            if first:
                reply_message = reply_message + subreddit_object.name
                first = False
            else:
                reply_message = reply_message + ", " + subreddit_object.name

        message.reply(reply_message)
        return

    def process_add_subreddit(self, message, redditter_object):
        print "Adding subreddit"
        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        for i in range(2, len(words)):
            subreddit = words[i]
            redditter_object.add_subreddit(subreddit)

        message.reply("Your requested subreddits have been added")
        return

    def process_remove_subreddit(self, message, redditter_object):
        print "Removing subreddit"
        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        for i in range(2, len(words)):
            subreddit = words[i]
            redditter_object.remove_subreddit(subreddit)

        message.reply("Your requested subreddits have been removed")
        return

    def process_get_keyword(self, message, redditter_object):
        print "Getting keyword"
        # Get body of message and split into words

        reply_message = "Your keywords: "
        first = True

        for keyword in redditter_object.keyword_list:
            if first:
                reply_message = reply_message + keyword
                first = False
            else:
                reply_message = reply_message + ", " + keyword

        message.reply(reply_message)
        return

    def process_add_keyword(self, message, redditter_object):
        print "Adding keyword"
        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        for i in range(2, len(words)):
            keyword = words[i]
            redditter_object.add_global_keyword(keyword)

        message.reply("Your requested keywords have been added")
        return

    def process_remove_keyword(self, message, redditter_object):
        print "Removing keyword"
        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        for i in range(2, len(words)):
            keyword = words[i]
            redditter_object.remove_global_keyword(keyword)

        message.reply("Your requested keywords have been removed")
        return

    def process_subscribe(self, message, redditter_object):
        print "Subscribing " + redditter_object.name
        redditter_object.subscribed = True

        message.reply("You have successfully subscribed to the News Bot.  Thank you for the interest.  Send 'unsubscribe' if you no longer wish to receive messages.")
        return

    def process_unsubscribe(self, message, redditter_object):
        print "Unsubscribing " + redditter_object.name
        redditter_object.subscribed = False

        message.reply("You have successfully subscribed to the News Bot.  Thank you for the interest.  Send 'unsubscribe' if you no longer wish to receive messages.")
        return

    def process_clear(self, message, redditter_object):
        print "Clearing all data"
        return

    def process_unknown(self, message, redditter_object):
        print "Unknown command processed"
        body = "I am unable to process your command.  Here is a list of available commands: "
        for menu in self.command_menu:
            (command, text) = menu
            body = body + command + ", "

        message.reply(body)
        return