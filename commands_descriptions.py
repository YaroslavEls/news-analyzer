class BotCommandsDescriptions:
    def __init__(self):
        # self.ready = 'Bot is ready!'

        self.resources = 'List of supported resources'
        self.is_true = 'Check if the article is true'
        self.analyze = 'Analyze articles over a specific period of time'
        self.find = 'Find and analyze articles by topic'

        self.link_arg = 'Url address of the article (must be from supported resources)'
        self.start_arg = 'Start date for selecting articles in format dd.mm.yyyy'
        self.end_arg = 'End date for selecting articles in format dd.mm.yyyy'
        self.topic_arg = 'Topic of interest'