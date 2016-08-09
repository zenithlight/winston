import argparse
import blinker

def command(name, description, initialize_command):
    def decorator(constructor):
        def wrapper(self, client):
            constructor(self, client)
            self.argument_parser = argparse.ArgumentParser(description=description, prog=name)
            initialize_command(self)

            def listen_for_command(sender, **kw):
                print('fsfsdhjkhjkfsd')
                print(message, command, arguments)
                if command == name:
                    self.invoke(message, arguments)

            blinker.signal('command').connect(listen_for_command)
        return wrapper
    return decorator
