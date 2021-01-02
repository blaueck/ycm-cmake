from .cmake_completor import CMakeCompleter


def GetCompleter(user_options):
    return CMakeCompleter(user_options)
