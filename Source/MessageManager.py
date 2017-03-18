import time
import prawcore.exceptions as PExceptions
__author__ = 'Evan'


'''
structure:

commands:
add keyword(s)   [data list]
add subreddit(s) [data list]
add time(s)      [data list]
add keyword(s)   [data list] subreddit(s) [data list]
add subreddit(s) [data list] keyword(s)   [data list]

remove keyword(s)   [data list]
remove subreddit(s) [data list]
remove time(s)      [data list]
remove keyword(s)   [data list] subreddit(s) [data list]
remove subreddit(s) [data list] keyword(s)   [data list]

get keyword(s)           [data list]
get subreddit(s)         [data list]
get time(s)              [data list]
get subreddit keyword(s) [data]

subscribe
unsubscribe
clear
help


-data can be either comma delimited, or space delimited, but comma delimited will include any spaces, minus any
leading/trailing spaces

- list of command word 2:
    -keyword(s)
    -subreddit(s)
    -time(s)
    -subreddit
'''

'''
Command:
    -Instruction
    -Data
-Split message into list of commands
    -
-Perform action based on command
-
'''


class Command:
    def __init__(self, instruction):

        self.instruction = instruction
        self.data = []

    def get_instruction_string(self):
        return self.instruction

    def add_data(self, word):
        self.data.append(word)

    def get_data(self):
        return self.data


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

        reply = ""

        # There are a few one word instructions, so process these
        if len(words) == 1:
            instruction = words[0]

            if instruction.lower() == "help":
                reply = self.process_help(message, redditter_object, None)
            elif instruction.lower() == "unsubscribe":
                reply = self.process_subscribe(message, redditter_object)
            elif instruction.lower() == "subscribe":
                reply = self.process_unsubscribe(message, redditter_object)
            elif instruction.lower() == "clear":
                reply = self.process_clear(message, redditter_object)
            else:
                reply = self.process_unknown(message, redditter_object)

        # These are two word instructions.
        elif len(words) >= 2:
            instruction = words[0]

            if instruction.lower() == "help":
                command = words[1]
                if len(words) >= 3:
                    command = command + " " + words[2]

                reply = self.process_help(message, redditter_object, command)
            elif instruction.lower() == "get":
                second_instruction = words[1]

                if second_instruction.lower() == "subreddit":
                    reply = self.process_get_subreddits(message, redditter_object)
                elif second_instruction.lower() == "subreddits":
                    reply = self.process_get_subreddits(message, redditter_object)
                elif second_instruction.lower() == "keyword":
                    reply = self.process_get_keyword(message, redditter_object)
                elif second_instruction.lower() == "keywords":
                    reply = self.process_get_keyword(message, redditter_object)
                else:
                    reply = self.process_unknown(message, redditter_object)

            elif instruction.lower() == "add":
                print "First instruction is add"
                # If the instruction is add, then the next instruction is either subreddit or keyword
                if len(words) >= 3:
                    second_instruction = words[1]

                    if second_instruction.lower() == "subreddit":
                        reply = self.process_add_subreddit(message, redditter_object)
                    elif second_instruction.lower() == "subreddits":
                        reply = self.process_add_subreddit(message, redditter_object)
                    elif second_instruction.lower() == "keyword":
                        reply = self.process_add_keyword(message, redditter_object)
                    elif second_instruction.ower() == "keywords":
                        reply = self.process_add_keyword(message, redditter_object)
                    else:
                        reply = self.process_unknown(message, redditter_object)

            elif instruction.lower() == "remove":
                print "First instruction is remove"
                # If the instruction is add, then the next instruction is either subreddit or keyword
                if len(words) >= 3:
                    second_instruction = words[1]

                    if second_instruction.lower() == "subreddit":
                        reply = self.process_remove_subreddit(message, redditter_object)
                    elif second_instruction.lower() == "subreddits":
                        reply = self.process_remove_subreddit(message, redditter_object)
                    elif second_instruction.lower() == "keyword":
                        reply = self.process_remove_keyword(message, redditter_object)
                    elif second_instruction.ower() == "keywords":
                        reply = self.process_remove_keyword(message, redditter_object)
                    else:
                        reply = self.process_unknown(message, redditter_object)
            else:
                reply = self.process_unknown(message, redditter_object)

        sent = False
        wait_times = [1, 2, 4, 8, 16, 32]
        index = 0
        while not sent:
            try:
                message.reply(reply)
                sent = True
            except PExceptions.RequestException:
                print "Request Exception handled in replying to a message"
                if index >= len(wait_times):
                    break
                sleep_time = wait_times[index]
                time.sleep(sleep_time)
                index += 1

    def process_help(self, message, redditter_object, command):
        reply_message = ""
        if command is not None:
            for item in self.command_menu:
                (menu, help_text) = item
                if command.lower() == menu.lower():
                    reply_message = command + ": " + help_text
        if reply_message == "":
            first = True

            reply_message = "Here are the commands I accept: "
            for item in self.command_menu:
                (menu, help_text) = item

                if first:
                    reply_message = reply_message + menu
                    first = False
                else:
                    reply_message = reply_message + ", " + menu

        return reply_message

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

        return reply_message

    def process_add_subreddit(self, message, redditter_object):
        print "Adding subreddit"
        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        for i in range(2, len(words)):
            subreddit = words[i]
            redditter_object.add_subreddit(subreddit)

        return "Your requested subreddits have been added"

    def process_remove_subreddit(self, message, redditter_object):
        print "Removing subreddit"
        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        for i in range(2, len(words)):
            subreddit = words[i]
            redditter_object.remove_subreddit(subreddit)

        return "Your requested subreddits have been removed"

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

        return reply_message

    def process_add_keyword(self, message, redditter_object):
        print "Adding keyword"
        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        for i in range(2, len(words)):
            keyword = words[i]
            redditter_object.add_global_keyword(keyword)

        return "Your requested keywords have been added"

    def process_remove_keyword(self, message, redditter_object):
        print "Removing keyword"
        # Get body of message and split into words
        text = message.body
        words = text.split(' ')

        for i in range(2, len(words)):
            keyword = words[i]
            redditter_object.remove_global_keyword(keyword)

        return "Your requested keywords have been removed"

    def process_subscribe(self, message, redditter_object):
        print "Subscribing " + redditter_object.name
        redditter_object.subscribed = True

        return"You have successfully subscribed to the News Bot.  Thank you for the interest.  Send 'unsubscribe' if you no longer wish to receive messages."

    def process_unsubscribe(self, message, redditter_object):
        print "Unsubscribing " + redditter_object.name
        redditter_object.subscribed = False

        return "You have successfully subscribed to the News Bot.  Thank you for the interest.  Send 'unsubscribe' if you no longer wish to receive messages."

    def process_clear(self, message, redditter_object):
        print "Clearing all data"
        return ""

    def process_unknown(self, message, redditter_object):
        print "Unknown command processed"

        first = True

        reply_message = "I am unable to process your command.  Here is a list of available commands: "
        for menu in self.command_menu:
            (command, text) = menu
            if first:
                reply_message = reply_message + command + ", "
                first = False
            else:
                reply_message = reply_message + ", " + command

        return reply_message

