__author__ = 'Evan'


class ParserException(Exception):
    def __init__(self, message):
        self.message = message
class Data:
    commands = ["Subscribe",
                "Unsubscribe",
                "Clear",
                "Add Subreddit",
                "Remove Subreddit",
                "Get Subreddit",
                "Add Subreddits",
                "Remove Subreddits",
                "Get Subreddits",
                "Add Keyword",
                "Remove Keyword",
                "Get Keyword",
                "Add Keywords",
                "Remove Keywords",
                "Get Keywords",
                "Add Time",
                "Remove Time",
                "Get Time",
                "Add Times",
                "Remove Times",
                "Get Times"]

    options = ["subreddit",
               "subreddits",
               "keyword",
               "keywords",
               "time",
               "times"]


class Token:
    COMMAND    = 1
    OPTION     = 2
    WORD       = 3
    WORD_COMMA = 4

    def __init__(self, identifier, data):
        self.identifier = identifier
        self.data = data


class Command:
    def __init__(self, command, data, options):
        self.command = command
        self.data = data
        self.options = options


class Lexer:
    def __init__(self):

        # Lists of instructions and options created from data
        self.commands = []
        self.options = []

        # Create list of instructions based on Data class
        for command in Data.commands:
            data = command.split(' ')
            for word in data:
                if word not in self.commands:
                    self.commands.append(word)

        # Create list of options based on Data class
        for option in Data.options:
            word = "-" + option
            self.options.append(word)

    def get_tokens(self, message):
        # Split message into words
        words = message.split(" ")

        # List of tokens to return
        tokens = []

        # Iterate over all words and get token from word
        for word in words:
            tokens.append(self.word_to_token(word))

        # Return list of tokens
        return tokens

    def word_to_token(self, word):
        token = None

        # Check if word matches an instruction
        for instruction in self.commands:
            if instruction.lower() == word.lower():
                token = Token(Token.COMMAND, word)

        # Check if word matches an option
        for option in self.options:
            if option.lower() == word.lower():
                token = Token(Token.OPTION, word)

        # Assume word is a word token if not a token already
        if token is None:
            if word.endswith(','):
                token = Token(Token.WORD_COMMA, word.rstrip(','))
            else:
                token = Token(Token.WORD, word)

        # Return token
        return token


class Parser:

    def __init__(self):
        # Create list of commands and options based on data
        self.valid_commands = list(Data.commands)
        self.valid_options = list(Data.options)

    def token_to_command(self, tokens):
        # Determine if message starts with command
        if len(tokens) > 0:
            if tokens[0].identifier != Token.COMMAND:
                raise ParserException("No Command")

        longest_command_length = self.get_longest_command_length()

        # Determine if message contains enough data
        if longest_command_length >= len(tokens):
            raise ParserException("No Data")

        print longest_command_length
        
        # Determine if message is valid
        if not self.is_valid_command(tokens):
            raise ParserException("Invalid Command")

        # Update non-command words identified as commands to words
        for i in range(longest_command_length, len(tokens)):
            if tokens[i].identifier == Token.COMMAND:
                tokens[i].identifier = Token.WORD

        # Condense command tokens into a single command token
        command_token = Token(Token.COMMAND, "")

        for token in tokens[0:longest_command_length]:
            command_token.data = command_token.data + " " + token.data

        command_token.data = command_token.data.lstrip(' ')
        tokens = [command_token] + tokens[longest_command_length:]
        
        # Split tokens into groups delimited by commands and options

        # For each group, determine if comma separated.  If comma separated, combine words between commas

        # Convert groups into command class

    def get_longest_command_length(self):
        # Set longest length to 0 initially
        longest_command_length = 0

        # Iterate over all valid commands to find longest one
        for valid_command in self.valid_commands:

            # Split command into words and get length
            command_words = valid_command.split(' ')
            command_length = len(command_words)

            # Update longest command length if current command is longer
            if command_length > longest_command_length:
                longest_command_length = command_length

        return longest_command_length

    def is_valid_command(self, tokens):
        # Setup data for checking for valid command
        is_valid_command = False
        longest_command_length = self.get_longest_command_length()
        command = ""

        # Get command from tokens
        for i in range(0, longest_command_length):
            command = command + " " + tokens[i].data

        # Strip leading space
        command = command.lstrip(' ')
        
        # Check each command
        for valid_command in self.valid_commands:
            if command.lower() == valid_command.lower():
                is_valid_command = True

        return is_valid_command

    def split_tokens_into_groups(self, tokens):
        indexes = []
