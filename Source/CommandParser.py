__author__ = 'Evan'


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

    # Codes for handling issues
    NO_COMMAND = 0
    INVALID_COMMAND = 1
    NO_COMMAND_DATA = 2
    NO_OPTION_DATA = 3

    def __init__(self):
        # Create list of commands and options based on data
        self.valid_commands = list(Data.commands)
        self.valid_options = list(Data.options)

    def token_to_command(self, tokens):
        command = None

        # Get combined instruction
        instruction = ""
        for i in range(0, len(tokens)):
            token = tokens[i]
            if token.identifier == Token.COMMAND:
                # Create multi-word instruction
                if i == 0 or i == 1:
                    instruction = instruction + token.data
                else:
                    token.identifier = Token.WORD
            if i == 0:
                if token[0] == Token.COMMAND:
                    instruction = token[1]
        return

    def condense_tokens(self, tokens):
        command_token = Token(Token.COMMAND, "")
        command_data = Token(Token.WORD, "")
        options_list = []

        step = Token.COMMAND

        # Condense commands
        for token in tokens:
            # Previous token was command or starting at beginning of token list
            if step == Token.COMMAND:
                if token.identifier == Token.COMMAND:
                    command_token.data = (command_token.data + " " + token.data).lstrip(" ")
                elif token.identifier in (Token.WORD, Token.WORD_COMMA):
                    command_data.data = (command_data.data + " " + token.data).lstrip(" ")
                    step = Token.WORD
                else:
                    raise Exception("Invalid Structure")
            elif step == Token.WORD:
                if token.identifier in (Token.COMMAND, Token.WORD, Token.WORD_COMMA):
                    return
    # Determines if message is valid
    def is_valid(self, tokens):
        command = ""
        command_found = False
        for i in range(0, tokens):
            token = tokens[i]

            # Checks
            if not command_found and i < 2:
                command = command + " " + token.data
                command.lstrip(" ")
                if self.is_command(command):
                    command_found = True

    def is_command(self, data):
        for command in self.valid_commands:
            if data.lower() == command.lower():
                return True

        return False

    # Used to determine whether to combine words or not
    def is_comma_separated(self, tokens):
        for token in tokens:
            if token.identifier == Token.WORD_COMMA:
                return True
        return False

    # Used to find continuous spans of data
    def find_non_word_indexes(self, tokens):
        indexes = []
        for i in range(0, tokens):
            token = tokens[i]
            if (token.identifier != Token.WORD) or (token.identifier != Token.WORD_COMMA):
                indexes.append(i)
        return indexes
