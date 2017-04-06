import time
import prawcore.exceptions as PExceptions
import Source.CommandParser as Parser
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


class MessageCommand:
    def __init__(self, command, description, callback):
        self.command = command
        self.description = description
        self.callback = callback


class MessageManager:
    def __init__(self):
        # Commands used for help
        self.command_menu = [MessageCommand("Help", "You're using this command dumbass.", self.process_help),
                             MessageCommand("Subscribe", "Subscribes to the bot.", self.process_subscribe),
                             MessageCommand("Unsubscribe", "Unsubscribes from the bot.  Any data will be kept for future use.", self.process_unsubscribe),
                             MessageCommand("Clear", "Clears data associated with your account.", self.process_clear),
                             MessageCommand("Add Subreddit", "Adds a list of subreddits to check.", self.process_add_subreddit),
                             MessageCommand("Add Subreddits", "Adds a list of subreddits to check.", self.process_add_subreddit),
                             MessageCommand("Get Subreddit", "Gets a list of subreddits to check.", self.process_get_subreddit),
                             MessageCommand("Get Subreddits", "Gets a list of subreddits to check.", self.process_get_subreddit),
                             MessageCommand("Remove Subreddit", "Adds a list of subreddits to check.", self.process_remove_subreddit),
                             MessageCommand("Remove Subreddits", "Adds a list of subreddits to check.", self.process_remove_subreddit),
                             MessageCommand("Add Keyword", "Adds a list of keywords to check.", self.process_add_keyword),
                             MessageCommand("Add Keywords", "Adds a list of keywords to check.", self.process_add_keyword),
                             MessageCommand("Get Keyword", "Gets a list of keywords to check.", self.process_get_keyword),
                             MessageCommand("Get Keywords", "Gets a list of keywords to check.", self.process_get_keyword),
                             MessageCommand("Remove Keyword", "Adds a list of keywords to check.", self.process_remove_keyword),
                             MessageCommand("Remove Keywords", "Adds a list of keywords to check.", self.process_remove_keyword),
                             MessageCommand("Add Times", "Adds a list of subreddits to check.", None),
                             MessageCommand("Get Time", "Gets a list of subreddits to check.", None),
                             MessageCommand("Get Times", "Gets a list of subreddits to check.", None),
                             MessageCommand("Remove Time", "Adds a list of subreddits to check.", None),
                             MessageCommand("Remove Times", "Adds a list of subreddits to check.", None)]

        # Initialize parser data
        Parser.Data.init()

        # Use command menu above to add commands
        for command in self.command_menu:
            Parser.Data.add_command(command.command)

        # Add options
        Parser.Data.add_option("subreddit")
        Parser.Data.add_option("subreddits")
        Parser.Data.add_option("keyword")
        Parser.Data.add_option("keywords")
        Parser.Data.add_option("time")
        Parser.Data.add_option("times")

        self.lexer = Parser.Lexer()
        self.parser = Parser.Parser()

        return

    def process_message(self, message, redditter_object):

        # Get command from body of message
        tokens = self.lexer.get_tokens(message.body)
        command = self.parser.token_to_command(tokens)

        # Get command and initialize reply
        commandName = command.command.lower()
        reply = None

        # There are a few one word instructions, so process these
        for menu in self.command_menu:
            if commandName == menu.command.lower():
                reply = menu.callback(message, redditter_object)
                break

        if reply is None:
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

    def process_help(self, message, redditter_object):
        reply_message = ""
        command = None
        if command is not None:
            for item in self.command_menu:

                if command.lower() == item.command.lower():
                    reply_message = command + ": " + item.description

        if reply_message == "":
            reply_message = "I am unable to process your command.  Here is a list of available commands: "

            for item in self.command_menu:
                reply_message = reply_message + "\n\n" + item.command

        return reply_message

    def process_get_subreddit(self, message, redditter_object):
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

        reply_message = "I am unable to process your command.  Here is a list of available commands: "

        for item in self.command_menu:
            reply_message = reply_message + "\n\n-" + item.command

        return reply_message

