class BotCommandsDescriptions:
    def __init__(self):
        self.resources = 'List of supported resources'
        self.resource_info = 'Information abour the resource \and it\'s recent activity'
        self.is_true = 'Check if the article is true'
        self.analyze = 'Analyze articles over a specific period of time'
        self.find = 'Find and analyze articles by topic'
        
        self.resource_id_arg = 'Id of the resource. *(resource\'s ids can be found with /resources command)'
        self.link_arg = 'Url address of the article (must be from supported resources)'
        self.start_arg = 'Start date for selecting articles in format dd.mm.yyyy'
        self.end_arg = 'End date for selecting articles in format dd.mm.yyyy'
        self.topic_arg = 'Topic of interest'
