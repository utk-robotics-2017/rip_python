class Component:
    def __init__(self):
        pass

    def get_command_parameters(self):
        raise NotImplementedError("Error: get_command_paramters")

    def run_tests(self):
        raise NotImplementedError("Error: run_tests")

    def show_suggestions(self):
        raise NotImplementedError("Error: show_suggestions")
