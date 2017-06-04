import os
import json
import getpass
from ..appendages.utils.decorators import type_check, attr_check, void, singleton
from .state import State
from .no_state_exception import NoStateException


@singleton
@attr_check
class StateMachine(object):

    __current_state = (None, State)
    state_file = str
    state_variables = dict
    state_map = dict

    def __new__(cls):
        return object.__new__(cls)

    @type_check
    def __init__(self):
        self.create_state_file()
        self.__current_state = None
        self.current_state = property(self.get_current_state, self.set_current_state)
        self.state_variables = {}

    def get_current_state(self):
        return self.__current_state

    def set_current_state(self, state):
        self.__current_state = state
        if state is not None:
            self.state_variables['current_state'] = state.name
            self.save_state()

    @type_check
    def create_state_file(self) -> void:
        program = os.path.basename(__file__)[:-3]  # remove .py
        user = getpass.getuser()
        self.state_file = ("/{0:s}_{1:s}.state").format(program, user)

    @type_check
    def set_state_map(self, state_map) -> void:
        self.state_map = state_map

    @type_check
    def load_state(self) -> void:
        # file does not exist
        if not os.path.isfile(self.state_file):
            return None

        if not hasattr(self, 'state_map'):
            raise Exception('No state map')

        # file exists
        with open(self.state_file) as f:
            text = f.read()
        self.state_variables = json.loads(text)
        self.current_state = self.state_map[self.state_variables['current_state']]

    @type_check
    def save_state(self) -> void:
        with open(self.state_file, 'w') as f:
            f.write(json.dumps(self.state_variables, sort_keys=True, indent=4))

    @type_check
    def remove_state_file(self) -> void:
        os.remove(self.state_file)

    @type_check
    def set_state(self, state) -> void:
        self.current_state = state

    @type_check
    def start(self, state_variables: dict) -> void:
        if self.current_state is None:
            raise NoStateException()

        if self.state_variables is None:
            self.state_variables = state_variables

        while True:
            self.state_variables.update(self.current_state.run())
            self.current_state = self.current_state.next_state(self.state_variables)
            if self.current_state is None:
                break
