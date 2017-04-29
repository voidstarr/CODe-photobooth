import ConfigParser


class Config(object):

    def __init__(self, config_file, section):
        self.section = section
        self.config_file = config_file
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)

    def get(self, key):
        return self.config.get(self.section, key)

    def getint(self, key):
        return self.config.getint(self.section, key)

    def getfloat(self, key):
        return self.config.getfloat(self.section, key)

    def getboolean(self, key):
        return self.config.getboolean(self.section, key)
