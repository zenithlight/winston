import argparse

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message): # prevent parser from calling sys.exit() on parse failure
        raise ValueError(message)
