from discord.app_commands import AppCommandError


class UserInputError(AppCommandError):
    def __init__(self, code):
        self.error_codes = {
            101: 'The link must contain a valid url address',
            102: 'Dates do not match required format: dd.mm.yyyy',
            103: 'The start date must be less than the end date',
            104: 'The topic must contain Latin or Cyrillic characters',
            105: 'Invalid resource_id',
        }
        self.message = self.error_codes[code]
        super().__init__(self.message)
