import os
import time
import praw
import Redditor


class Bot:
    def __init__(self, name):
        # Get news bot with login info for account
        self.reddit = praw.Reddit(name)

        # Get list of folders for redditors and messages
        self.redditor_folder = "redditors.txt"
        self.message_folder = "message_id.txt"

        # Create list of Redditers using this bot and message ids
        self.redditter_list = []
        self.redditter_object_list = []
        self.message_id_list = []
        self.message_list = []

        # Commands used for help
        self.command_menu = [("Subscribe", "Subscribes to the bot.  If you had a list of keywords and subreddits, these will be retained"),
                             ("Unsubscribe", "Unsubscribes from the bot.  This will keep your list of keywords and subreddits"),
                             ("Clear", "Clears list of subreddits and keywords"),
                             ("Add Subreddit", "Adds a single subreddit this bot will check."),
                             ("Remove Subreddit", "Removes a single subreddit from your list of subreddits this bot checks."),
                             ("Add Subreddits", "Adds multiple subreddits this bot will check."),
                             ("Remove Subreddits", "Removes multiple subreddits from your list of subreddits this bot checks."),
                             ("Add Keyword", "Adds a single keyword to check in the list of subreddits."),
                             ("Remove Keywords", "Removes a single keyword from your list of keywords."),
                             ("Add Keywords", "Adds multiple keywords to check in the list of subreddits."),
                             ("Remove Keywords", "Removes multiple keywords from your list of keywords.")]

        self.load()

    def run(self):
        # Indexes for hours and minutes
        hours_index = 3
        minutes_index = 4

        # Get last run time
        current_time = time.gmtime()
        previous_hours = current_time[hours_index]
        previous_minutes = current_time[minutes_index]

        # Start running
        while True:
            try:
                # Get current time
                current_time = time.gmtime()

                if current_time[minutes_index] != previous_minutes:
                    # Update previous minutes to current minutes
                    previous_minutes = current_time[minutes_index]

                    # Get messages and process them
                    messages = self.reddit.inbox.all(limit=25)
                    for item in messages:
                        if item.id not in self.message_id_list:
                            print "New Message received"
                            # Only look at ids not already found
                            self.message_id_list.append(item.id)

                            self.process_message(item)

                    print "Messages processed"

                    self.save()

                if (current_time[hours_index] != previous_hours) and (current_time[hours_index] % 8 == 0):
                    # Update previous hours to current hours
                    previous_hours = current_time[hours_index]

                    # Get posts and send if updated
                    for account in self.redditter_object_list:
                        account.process_posts(self.reddit, 100)
                        account.save()

                    print "Posts processed"

                time.sleep(5)
            except:
                time.sleep(10)

    def process_message(self, message):
        # Get sender of message
        redditer_name = message.author
        redditter_object = self.get_redditer_object(redditer_name)

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

                if second_instruction == "subreddit":
                    self.process_get_subreddits(message, redditter_object)
                elif second_instruction == "subreddits":
                    self.process_get_subreddits(message, redditter_object)
                elif second_instruction == "keyword":
                    self.process_get_keyword(message, redditter_object)
                elif second_instruction == "keywords":
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

            elif instruction.lower() is "remove":
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

        reply_message = "Your subreddits:"

        for subreddit in redditter_object.subreddit_list:
            reply_message = reply_message + ", " + subreddit

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

        reply_message = "Your keywords:"

        for keyword in redditter_object.keyword_list:
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
            redditter_object.add_keyword(keyword)

        message.reply("Your requested keywords have been added")
        return

    def process_remove_keyword(self, message, redditter_object):
        print "Removing keyword"
        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        for i in range(2, len(words)):
            keyword = words[i]
            redditter_object.remove_keyword(keyword)

        message.reply("Your requested keywords have been removed")
        return

    def process_subscribe(self, message, redditter_object):
        redditter_object.subscribed = True

        message.reply("You have successfully subscribed to the News Bot.  Thank you for the interest.  Send 'unsubscribe' if you no longer wish to receive messages.")
        return

    def process_unsubscribe(self, message, redditter_object):
        redditter_object.subscribed = False

        message.reply("You have successfully subscribed to the News Bot.  Thank you for the interest.  Send 'unsubscribe' if you no longer wish to receive messages.")
        return

    def process_clear(self, message, redditter_object):
        return

    def process_unknown(self, message, redditter_object):
        body = "I am unable to process your command.  Here is a list of available commands: "
        for menu in self.command_menu:
            (command, text) = menu
            body = body + command + ", "

        message.reply(body)
        return

    def get_redditer_object(self, name):
        redditter = None
        if name in self.redditter_list:
            for redditer_object in self.redditter_object_list:
                if name == redditer_object.name:
                    redditter = redditer_object
        else:
            self.redditter_list.append(name)
            redditter_object = Redditor.AccountManager(self.reddit, name, True)
            redditter = redditter_object
            self.redditter_object_list.append(redditter_object)

        return redditter

    def load(self):
        # Initialize object list to empty
        self.redditter_object_list = []

        # Open list of redditers. If no file exists, create it
        if not os.path.isfile(self.redditor_folder):
            self.redditter_list = []
        else:
            with open(self.redditor_folder, "r") as f:
                redditors = f.read()
                redditors = redditors.split("\n")
                self.redditter_list = list(filter(None, redditors))

        # Open list of message ids. If no file exists, create it
        if not os.path.isfile(self.message_folder):
            self.message_id_list = []
        else:
            with open(self.message_folder, "r") as f:
                message_ids = f.read()
                message_ids = message_ids.split("\n")
                self.message_id_list = list(filter(None, message_ids))

        for redditor in self.redditter_list:
            self.redditter_object_list.append(Redditor.AccountManager(self.reddit, redditor, True))
        return

    def save(self):
        with open(self.redditor_folder, "w") as f:
            for redditer in self.redditter_list:
                f.write(redditer + "\n")

        with open(self.message_folder, "w") as f:
            for message_id in self.message_id_list:
                f.write(message_id + "\n")
        return

NewsBot = Bot("newsbot")

NewsBot.run()
