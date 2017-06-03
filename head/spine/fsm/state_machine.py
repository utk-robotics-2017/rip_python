import os


class StateMachine(object):
    def __init__(self):
        self.create_state_file()
        self.current_state = None
        self.state_variables = {}

    def create_state_file(self):
        program = os.path.basename(__file__)[:-3]  # remove .py
        user = getpass.getuser()
        self.state_file = ("/{0:s}_{1:s}.state").format(program, user)

    def set_state_map(self, state_map):
        self.state_map = state_map

    def load_state(self):
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

    def save_state(self):
        with open(self.state_file, 'w') as f:
            f.write(json.dumps(self.state_variables, sort_keys=True, indent=4))

    def remove_state_file(self):
        os.remove(self.state_file)

    def set_state(self, state):
        self.current_state = state

    def start(self, state_variables):
        if self.current_state is None:
            raise NoStateException()

        if self.state_variables is None:
            self.state_variables = state_variables

        while True:
            self.state_variables.update(self.current_state.run())
            self.current_state = self.current_state.next_state(self.state_variables)
            if self.current_state is None:
                break

    def __setattr__(self, k, v):
        # on state change save
        if k == 'current_state':
            self.state_variables['current_state'] = v.name
            self.save_state()

        # Normal
        self.__dict__[k] = v
