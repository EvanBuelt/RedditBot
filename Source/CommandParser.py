__author__ = 'Evan'


class ParserException(Exception):
    def __init__(self, message):
        self.message = message


class Data:

    commands = []
    options = []

    @classmethod
    def init(cls):
        cls.commands = []
        cls.options = []

    @classmethod
    def add_command(cls, command):
        cls.commands.append(command)

    @classmethod
    def add_option(cls, option):
        cls.options.append(option)


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
        # Ensure there's data to be parsed
        if len(tokens) == 0:
            raise ParserException("No Data")

        # Determine if message starts with command
        self._check_for_command(tokens)
        
        # Determine if message is valid
        command = self._get_command(tokens)
        command_length = len(command.split(' '))

        # Update non-command words identified as commands to words
        for i in range(command_length, len(tokens)):
            if tokens[i].identifier == Token.COMMAND:
                tokens[i].identifier = Token.WORD

        # Condense command tokens into a single command token
        command_token = Token(Token.COMMAND, "")

        for token in tokens[0:command_length]:
            command_token.data = command_token.data + " " + token.data

        command_token.data = command_token.data.lstrip(' ')
        tokens = [command_token] + tokens[command_length:]

        # Split tokens into groups delimited by commands and options
        groups = self._split_tokens_into_groups(tokens)

        # For each group, determine if comma separated.  If comma separated, combine words between commas
        groups = self._filter_groups(groups)

        # Convert groups into command class
        command = self._create_command_object(groups)

        return command

    def _check_for_command(self, tokens):
        if tokens[0].identifier != Token.COMMAND:
            raise ParserException("No Command")

    def _get_longest_command_length(self):
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

    def _get_command(self, tokens):

        longest_command_length = self._get_longest_command_length()
        command = ""
        valid_command = False

        for i in range(0, longest_command_length):
            token = tokens[i]
            if token.identifier == Token.COMMAND:
                command = command + " " + tokens[i].data
                command = command.lstrip(' ')
                valid_command = self._is_valid_command(command)
                if valid_command:
                    break
            else:
                break

        if not valid_command:
            raise ParserException("Invalid Command")

        return command

    def _is_valid_command(self, command):
        is_valid_command = False

        # Check each command
        for valid_command in self.valid_commands:
            if command.lower() == valid_command.lower():
                is_valid_command = True

        return is_valid_command

    def _split_tokens_into_groups(self, tokens):
        indexes = []

        # List of tokens split into group
        group = []

        # Current group of instructions or
        current_group = []

        # Variable used for first group
        first = True

        for token in tokens:
            if token.identifier in [Token.COMMAND, Token.OPTION]:
                if not first:
                    group.append(current_group)
                else:
                    first = False
                current_group = list()
                current_group.append(token)
            elif token.identifier in [Token.WORD, Token.WORD_COMMA]:
                current_group.append(token)

        # Add last group (as there's no way to know in for loop)
        group.append(current_group)

        return group

    def _filter_groups(self, groups):
        new_groups = []
        for group in groups:
            has_commas = False
            new_group = []

            for token in group:
                if token.identifier == Token.WORD_COMMA:
                    has_commas = True

            if has_commas:
                condensed_token = Token(Token.WORD, "")
                token = Token(Token.WORD, "")

                # May want to use index to know when last word is reached
                for i in range(0, len(group)):
                    token = group[i]
                    if token.identifier in [Token.COMMAND, Token.OPTION]:
                        new_group.append(token)
                    elif token.identifier == Token.WORD:
                        condensed_token.data = condensed_token.data + " " + token.data
                    elif token.identifier == Token.WORD_COMMA:
                        condensed_token.data = condensed_token.data + " " + token.data
                        condensed_token.data = condensed_token.data.lstrip(' ')
                        condensed_token.data = condensed_token.data.rstrip(',')
                        new_group.append(condensed_token)
                        condensed_token = Token(Token.WORD, "")

                # Cleanup if last word in group has a comma
                if token.identifier == Token.WORD:
                    condensed_token.data = condensed_token.data.lstrip(' ')
                    condensed_token.data = condensed_token.data.rstrip(',')
                    new_group.append(condensed_token)

            else:
                new_group = group

            new_groups.append(new_group)

        return new_groups

    def _create_command_object(self, groups):
        command = Command("", [], [])
        group_type = Token.COMMAND
        option_data = []
        option = ""
        for group in groups:
            for token in group:
                if token.identifier == Token.COMMAND:
                    group_type = Token.COMMAND
                    command.command = token.data
                elif token.identifier == Token.OPTION:
                    group_type = Token.OPTION
                    option = token.data
                    option_data = []
                elif token.identifier in [Token.WORD, Token.WORD_COMMA]:
                    if group_type == Token.COMMAND:
                        command.data.append(token.data)
                    elif group_type == Token.OPTION:
                        option_data.append(token.data)

            if group_type == Token.OPTION:
                command.options.append([option, option_data])

        return command
