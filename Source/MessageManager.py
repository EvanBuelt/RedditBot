import Source.ExceptionHandler
import Source.CommandParser as Parser
import prawcore.exceptions as praw_exceptions
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
    def __init__(self, reddit):
        # Commands used for help
        self.command_menu = [MessageCommand("Help",              "You're using this command dumbass.",  self.process_help),
                             MessageCommand("Subscribe",         "Subscribes to the bot.",              self.process_subscribe),
                             MessageCommand("Unsubscribe",       "Unsubscribes from the bot.  Any data will be kept for future use.", self.process_unsubscribe),
                             MessageCommand("Clear",             "Clears data associated with your account.", self.process_clear),
                             MessageCommand("Add Subreddit",     "Adds a list of subreddits to check.", self.process_add_subreddit),
                             MessageCommand("Add Subreddits",    "Adds a list of subreddits to check.", self.process_add_subreddit),
                             MessageCommand("Get Subreddit",     "Gets a list of subreddits to check.", self.process_get_subreddit),
                             MessageCommand("Get Subreddits",    "Gets a list of subreddits to check.", self.process_get_subreddit),
                             MessageCommand("Remove Subreddit",  "Adds a list of subreddits to check.", self.process_remove_subreddit),
                             MessageCommand("Remove Subreddits", "Adds a list of subreddits to check.", self.process_remove_subreddit),
                             MessageCommand("Add Keyword",       "Adds a list of keywords to check.",   self.process_add_keyword),
                             MessageCommand("Add Keywords",      "Adds a list of keywords to check.",   self.process_add_keyword),
                             MessageCommand("Get Keyword",       "Gets a list of keywords to check.",   self.process_get_keyword),
                             MessageCommand("Get Keywords",      "Gets a list of keywords to check.",   self.process_get_keyword),
                             MessageCommand("Remove Keyword",    "Adds a list of keywords to check.",   self.process_remove_keyword),
                             MessageCommand("Remove Keywords",   "Adds a list of keywords to check.",   self.process_remove_keyword),
                             MessageCommand("Add Time",          "Adds a list of subreddits to check.", self.process_add_time),
                             MessageCommand("Add Times",         "Adds a list of subreddits to check.", self.process_add_time),
                             MessageCommand("Get Time",          "Gets a list of subreddits to check.", self.process_get_time),
                             MessageCommand("Get Times",         "Gets a list of subreddits to check.", self.process_get_time),
                             MessageCommand("Remove Time",       "Adds a list of subreddits to check.", self.process_remove_time),
                             MessageCommand("Remove Times",      "Adds a list of subreddits to check.", self.process_remove_time)]

        self.reddit = reddit
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
        try:
            tokens = self.lexer.get_tokens(message.body)
            command = self.parser.token_to_command(tokens)

            # Get command and initialize reply
            commandName = command.command.lower()
            reply = None

            # There are a few one word instructions, so process these
            for menu in self.command_menu:
                if commandName == menu.command.lower():
                    reply = menu.callback(command, redditter_object)
                    break

            if reply is None:
                reply = self.process_unknown(command, redditter_object)
        except Parser.ParserException:
            reply = self.process_unknown("Exception", redditter_object)

        Source.ExceptionHandler.praw_caller(message.reply, list(), "Exception handled in replying to a message", reply)

    def process_help(self, command, redditter_object):
        reply_message = ""
        command_word = ""
        for word in command.data:
            command_word = command_word + " " + word

        command_word = command_word.lstrip(" ")
        if command_word != "":
            for item in self.command_menu:
                if command_word.lower() == item.command.lower():
                    reply_message = command_word + ": " + item.description

        if reply_message == "":
            reply_message = "I am unable to process your command.  Here is a list of available commands: "

            for item in self.command_menu:
                reply_message = reply_message + "\n\n" + item.command

        return reply_message

    # Subreddit related functionality
    def process_get_subreddit(self, command, redditter_object):
        print "Getting subreddits"
        # Get body of message and split into words

        reply_message = "Your subreddits: "
        first = True

        for subreddit_object in redditter_object.get_subreddit_name_list():
            if first:
                reply_message = reply_message + subreddit_object.name
                first = False
            else:
                reply_message = reply_message + ", " + subreddit_object.name

        return reply_message

    def process_add_subreddit(self, command, redditter_object):
        print "Adding subreddit"
        # Get body of message and split into words
        words = command.data

        # List of added subreddits
        added_subreddits = []

        for word in words:
            subreddit_name = word

            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.new(limit=1)
                for item in posts:
                    item = item
            except praw_exceptions.Redirect:
                continue

            added_subreddits = added_subreddits + redditter_object.add_subreddit(subreddit_name)

        # Handle message back to redditter
        if len(added_subreddits) == 0:
            message = "No subreddits have been added."
        else:
            message = "The following subreddits have been added: "
            for i in range(0, len(added_subreddits)):
                message = message + "\n\n" + str(i + 1) + ") " + added_subreddits[i]
        return message

    def process_remove_subreddit(self, command, redditter_object):
        print "Removing subreddit"
        # Get body of message and split into words
        words = command.data

        # List of removed subreddits
        removed_subreddits = []

        for subreddit in words:
            removed_subreddits = removed_subreddits + redditter_object.remove_subreddit(subreddit)

        # Handle message back to redditter
        if len(removed_subreddits) == 0:
            message = "No subreddits have been removed."
        else:
            message = "The following subreddits have been removed: "
            for i in range(0, len(removed_subreddits)):
                message = message + "\n\n" + str(i + 1) + ") " + removed_subreddits[i]
        return message

    # Keyword related functionality
    def process_get_keyword(self, command, redditter_object):
        print "Getting keyword"
        # Get body of message and split into words

        reply_message = "Your keywords: "
        first = True

        for keyword in redditter_object.get_global_keyword_list():
            if first:
                reply_message = reply_message + keyword
                first = False
            else:
                reply_message = reply_message + ", " + keyword

        return reply_message

    def process_add_keyword(self, command, redditter_object):
        print "Adding keyword"
        # Get body of message and split into words
        words = command.data

        # List of added keywords
        added_keywords = []

        for keyword in words:
            added_keywords = added_keywords + redditter_object.add_global_keyword(keyword)

        if len(added_keywords) == 0:
            message = "No keywords have been added."
        else:
            message = "The following keywords have been added: "
            for i in range(0, len(added_keywords)):
                message = message + "\n\n" + str(i + 1) + ") " + added_keywords[i]
        return message

    def process_remove_keyword(self, command, redditter_object):
        print "Removing keyword"
        # Get body of message and split into words
        words = command.data

        # List of removed keywords
        removed_keywords = []

        for keyword in words:
            removed_keywords = removed_keywords + redditter_object.remove_global_keyword(keyword)

        if len(removed_keywords) == 0:
            message = "No keywords have been removed."
        else:
            message = "The following keywords have been removed: "
            for i in range(0, len(removed_keywords)):
                message = message + "\n\n" + str(i + 1) + ") " + removed_keywords[i]
        return message

    # Time related functionality
    def process_add_time(self, command, redditter_object):
        print "Adding time"

        list_of_times = self.get_list_of_times(command.data)
        list_of_converted_times = [self.convert_to_24_hour(unconverted_time) for unconverted_time in list_of_times]

        # Added times
        added_times = []

        for converted_time in list_of_converted_times:
            added_times = added_times + redditter_object.add_time(converted_time)

        if len(list_of_converted_times) == 0:
            return "Invalid time format.  Please use hh:mm am/pm (12 hour format) or hh:mm (24 hour format)"
        else:
            if len(added_times) == 0:
                message = "No times have been added."
            else:
                message = "The following times have been added: "
                for i in range(0, len(added_times)):
                    message = message + "\n\n" + str(i + 1) + ") " + added_times[i]
            return message

    def process_remove_time(self, command, redditter_object):
        print "Removing time"

        # Removed times
        removed_times = []

        list_of_times = self.get_list_of_times(command.data)
        list_of_converted_times = [self.convert_to_24_hour(unconverted_time) for unconverted_time in list_of_times]

        for converted_time in list_of_converted_times:
            removed_times = removed_times + redditter_object.remove_time(converted_time)

        if len(list_of_converted_times) == 0:
            return "Invalid time format.  Please use hh:mm am/pm (12 hour format) or hh:mm (24 hour format)"
        else:
            if len(removed_times) == 0:
                message = "No times have been removed."
            else:
                message = "The following times have been removed: "
                for i in range(0, len(removed_times)):
                    message = message + "\n\n" + str(i + 1) + ") " + removed_times[i]
            return message

    def process_get_time(self, command, redditter_object):
        print "Getting time"
        # Get body of message and split into words

        reply_message = "Your times: "
        first = True

        for time_hm in redditter_object.get_time_list():
            if first:
                reply_message = reply_message + time_hm
                first = False
            else:
                reply_message = reply_message + ", " + time_hm

        return reply_message

    def get_list_of_times(self, data_list):
        time_list = []
        current_time = ""

        first_part = ""
        second_part = ""

        for word in data_list:
            if first_part == "":
                first_part = word
            else:
                second_part = word
                if second_part.lower() in ["am", "pm"]:
                    current_time = first_part + " " + second_part
                    if self.is_valid_time(current_time):
                        time_list.append(current_time)
                    first_part = ""
                else:
                    if self.is_valid_time(first_part):
                        time_list.append(first_part)
                    first_part = second_part

        return time_list

    def is_valid_time(self, input_time):
        # If there are 2 words in unvalidated_time, then I assume it's 12-hour format
        unvalidated_time = input_time.split(' ')
        if len(unvalidated_time) == 2:
            # Format is (h)h:mm (a|p)m

            # Check for ":"
            if ":" not in unvalidated_time[0]:
                return False
            time_hm = unvalidated_time[0].split(':')

            # Verify there are only two numbers for hours and minutes section
            for word in time_hm:
                if len(word) > 2:
                    return False
                for char in word:
                    if not char.isdigit():
                        return False

            # Verify hours is between 1 and 12 inclusive, and minutes between 0 and 59 inclusive
            hours = time_hm[0]
            minutes = time_hm[1]

            if int(hours) < 1 or int(hours) > 12:
                return False

            if int(minutes) < 0 or int(minutes) > 59:
                return False

            # Check for am/pm
            if unvalidated_time[1].lower() not in ["am", "pm"]:
                return False

            return True

        elif len(unvalidated_time) == 1:
            # Format is (h)h:mm

            # Check for ":"
            if ":" not in unvalidated_time[0]:
                return False
            time_hm = unvalidated_time[0].split(':')

            # Verify there are only two numbers for hours and minutes section
            for word in time_hm:
                if len(word) > 2:
                    return False
                for char in word:
                    if not char.isdigit():
                        return False
            return True

        # Length of data is either 0 or more than 2, so not a valid time.
        return False

    def convert_to_24_hour(self, unconverted_time):
        validated_time = unconverted_time.split(" ")
        valid_time = ""
        if len(validated_time) == 1:
            valid_time = validated_time[0]
        elif len(validated_time) == 2:
            temp = validated_time[0].split(":")
            hours = temp[0]
            minutes = temp[1]

            if validated_time[1].lower() == "am":
                if hours == "12":
                    hours = "0"
            elif validated_time[1].lower() == "pm":
                if hours != "12":
                    hours = str(int(hours) + 12)

            valid_time = hours + ":" + minutes

        return valid_time

    # Subscription related functionality
    def process_subscribe(self, command, redditter_object):
        print "Subscribing " + redditter_object.name
        redditter_object.subscribed = True

        return"You have successfully subscribed to the News Bot.  Thank you for the interest.  Send 'unsubscribe' if you no longer wish to receive messages."

    def process_unsubscribe(self, command, redditter_object):
        print "Unsubscribing " + redditter_object.name
        redditter_object.subscribed = False

        return "You have successfully subscribed to the News Bot.  Thank you for the interest.  Send 'unsubscribe' if you no longer wish to receive messages."

    def process_clear(self, command, redditter_object):
        print "Clearing all data"
        return ""

    # Process unknown/invalid commands
    def process_unknown(self, command, redditter_object):
        print "Unknown command processed"

        reply_message = "I am unable to process your command.  Here is a list of available commands: "

        for item in self.command_menu:
            reply_message = reply_message + "\n\n-" + item.command

        return reply_message
