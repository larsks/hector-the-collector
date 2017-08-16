class HectorException(Exception):
    pass


class CLIError(HectorException):
    '''This represents an error that is meant to be presented
    to the user.'''

    pass


class ConfigurationError(CLIError):
    pass
