class Component:
    '''Base class for all RIP appendages'''
    # Constants for diagnostics
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

    def get_dependency_update(self):
        pass

    def sim_update(self, hal_data, tm_diff):
        pass

    def get_hal_data(self):
        raise NotImplementedError("Error: get_hal_data")
