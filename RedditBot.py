import time
import praw
import Source.Redditor
import Source.FileManager
import Source.MessageManager
import prawcore.exceptions as PExceptions


class Bot:
    def __init__(self, name):
        # Get news bot with login info for account
        self.reddit = praw.Reddit(name)

        # Get list of folders for redditors and messages
        self.redditor_folder = "data/redditors.txt"
        self.message_folder = "data/message_id.txt"

        # xml folder
        self.xml_folder = "data/redditors.xml"
        self.xml_loader = Source.FileManager.XmlLoader(self.xml_folder)
        self.xml_manager = Source.FileManager.XmlManager(self.xml_loader)

        # Create list of Redditers using this bot and message ids
        self.redditter_list = []
        self.redditter_object_list = []
        self.message_id_list = []
        self.message_list = []

        # Setup Message manager
        self.message_manager = Source.MessageManager.MessageManager()

        self.load()

    def run(self):
        # Indexes for hours and minutes
        hours_index = 3
        minutes_index = 4

        # Get last run time
        current_time = time.gmtime()
        previous_minutes = current_time[minutes_index]
        previous_hours = current_time[hours_index]

        # Start running
        while True:
            # Get current time
            current_time = time.localtime()
            try:
                if current_time[minutes_index] != previous_minutes:
                    # Update previous minutes to current minutes
                    previous_minutes = current_time[minutes_index]

                    # Get list of messages from inbox
                    messages = self.get_inbox_messages()

                    # Process messages
                    self.process_message(messages)

                    # Save in case data updated
                    self.save()
            except Exception as instance:
                print "Exception handled in checking inbox: ", type(instance), instance
                time.sleep(10)

            try:
                if (current_time[hours_index] != previous_hours) and (current_time[hours_index] % 4 == 0):
                    previous_hours = current_time[hours_index]
                    # Get posts and send if updated
                    for account in self.redditter_object_list:
                        account.process_posts(self.reddit, 100)
                    print "Posts processed"

            except Exception as instance:
                print "Exception handled in sending: ", type(instance), instance
                time.sleep(10)
            time.sleep(5)

    def get_inbox_messages(self):
        messages = []
        received = False
        wait_times = [1, 2, 4, 8, 16, 32]
        index = 0

        while not received:
            try:
                # Get messages and process them
                messages = self.reddit.inbox.all(limit=25)
                received = True
            except PExceptions.RequestException:
                print "Request Exception handled in getting inbox"
                if index >= len(wait_times):
                    break
                sleep_time = wait_times[index]
                time.sleep(sleep_time)
                index += 1
        return messages

    def process_message(self, message_list):
        for message in message_list:
            if message.id not in self.message_id_list:
                print "New Message received"
                # Only look at ids not already found
                self.message_id_list.append(message.id)

                # Get sender of message
                redditer_name = message.author
                redditter_object = self.get_redditer_object(redditer_name)

                # Process messages
                self.message_manager.process_message(message, redditter_object)

    def get_redditer_object(self, name):
        redditter = None
        if name in self.redditter_list:
            for redditer_object in self.redditter_object_list:
                if name == redditer_object.name:
                    redditter = redditer_object
        else:
            self.redditter_list.append(name)
            redditter_object = Source.Redditor.AccountManager(self.reddit, name, True)
            redditter = redditter_object
            self.redditter_object_list.append(redditter_object)

        return redditter

    def load(self):
        # Initialize object list to empty
        self.redditter_object_list = []

        # Load list of redditers and message ids
        self.redditter_list = Source.FileManager.load_id_list(self.redditor_folder)
        self.message_id_list = Source.FileManager.load_id_list(self.message_folder)

        print "Redditer List: ", self.redditter_list
        print "Message List: ", self.message_id_list

        for redditor in self.redditter_list:
            self.xml_manager.add_redditor(redditor)
            self.redditter_object_list.append(Source.Redditor.AccountManager(self.reddit, redditor, self.xml_manager))
        return

    def save(self):
        Source.FileManager.save_id_list(self.redditor_folder, self.redditter_list)
        Source.FileManager.save_id_list(self.message_folder, self.message_id_list)
        for account in self.redditter_object_list:
            account.save_version_0_1()
        return

NewsBot = Bot("newsbot")

NewsBot.run()
