import time
import praw
import Source.Redditor
import Source.FileManager
import Source.MessageManager
import Source.ExceptionHandler


class Bot:
    def __init__(self, name):
        # Get news bot with login info for account
        self.reddit = praw.Reddit(name)

        # xml folder
        self.xml_folder = "data/redditors.xml"
        self.xml_loader = Source.FileManager.XmlLoader(self.xml_folder)
        self.xml_manager = Source.FileManager.XmlManager(self.xml_loader)

        # Create list of Redditers using this bot and message ids
        self.redditter_list = []
        self.redditter_object_list = []
        self.message_list = []

        # Setup Message manager
        self.message_manager = Source.MessageManager.MessageManager(self.reddit)

        self.load()

    def run(self):
        # Indexes for hours and minutes
        hours_index = 3
        minutes_index = 4

        # Get last run time
        current_time = time.localtime()
        previous_minutes = current_time[minutes_index]
        previous_hours = current_time[hours_index]

        print "Initial minutes: ", previous_minutes
        print "Initial hours: ", previous_hours

        # Start running
        while True:
            # Get current time
            current_time = time.localtime()
            try:
                if current_time[minutes_index] != previous_minutes:
                    # Handles inbox messages sent to box
                    self.handle_inbox()

                    # Update previous minutes to current minutes
                    previous_minutes = current_time[minutes_index]

            except Exception as instance:
                print "Exception in handling inbox: ", type(instance), instance
                time.sleep(10)

            try:
                if (current_time[hours_index] != previous_hours) and (current_time[hours_index] % 4 == 0):
                    print previous_hours, current_time[hours_index]

                    # Get posts and send if updated
                    for account in self.redditter_object_list:
                        account.process_posts(self.reddit, 100)

                    previous_hours = current_time[hours_index]
                    print "Posts processed"

            except Exception as instance:
                print "Exception in sending messages: ", type(instance), instance
                time.sleep(10)
            time.sleep(5)

    def handle_inbox(self):

        # Get list of messages from inbox
        messages = Source.ExceptionHandler.praw_caller(self.get_inbox_messages, "Exception in getting inbox")

        # Process messages
        self.process_message(messages)

        # Save in case data updated
        self.save()

    def get_inbox_messages(self):
        messages = []

        # Get unread messages and process them
        unread_messages = self.reddit.inbox.unread(limit=25)
        inbox_messages = self.reddit.inbox.messages(limit=50)

        # Get any unread message in 'messages' inbox only
        for message in unread_messages:
            if message in inbox_messages:
                messages.append(message)

        return messages

    def process_message(self, message_list):
        for message in message_list:
            print "New Message received"

            # Get sender of message
            redditer_name = message.author
            redditter_object = self.get_redditer_object(redditer_name)

            # Process messages
            self.message_manager.process_message(message, redditter_object)

            # Mark message read
            Source.ExceptionHandler.praw_caller(message.mark_read, "Exception handled in marking message read")

    def get_redditer_object(self, name):
        redditter = None
        if name in self.redditter_list:
            for redditer_object in self.redditter_object_list:
                if name == redditer_object.name:
                    redditter = redditer_object
        else:
            self.redditter_list.append(name)
            redditter_object = Source.Redditor.AccountManager(self.reddit, name, self.xml_manager, True)
            redditter = redditter_object
            self.redditter_object_list.append(redditter_object)

        return redditter

    def load(self):

        # Initialize object list to empty
        self.redditter_object_list = []

        # Load list of redditers and message ids
        self.redditter_list = self.xml_manager.get_redditor_name_list()

        for redditor in self.redditter_list:
            redditor_object = Source.Redditor.AccountManager(self.reddit, redditor, self.xml_manager, False)
            self.xml_manager.add_redditor(redditor)
            self.redditter_object_list.append(redditor_object)

        print "Redditer List: ", self.redditter_list
        print "Redditor Object List: ", self.redditter_object_list

        return

    def save(self):
        for account in self.redditter_object_list:
            account.save_version_0_1()
        return

NewsBot = Bot("newsbot")

NewsBot.run()
