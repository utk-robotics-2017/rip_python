class Component:
    PASSED_TEST = 0
    FAILED_TEST = 1

    def __init__(self):
        pass

    def get_command_parameters(self):
        raise NotImplementedError("Error: get_command_paramters")

    def run_tests(self):
        raise NotImplementedError("Error: run_tests")

    def show_suggestions(self):
        raise NotImplementedError("Error: show_suggestions")

    def sim_update(self, tm_diff):
        pass
