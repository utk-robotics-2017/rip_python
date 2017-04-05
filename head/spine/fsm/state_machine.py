import os
import getpass

class StateMachine(object):
    def __init__(self):
        self.create_state_file()
        self.current_state = None

    def create_state_file(self):
        program = os.path.basename(__file__)[:-3]  # remove .py
        user = getpass.getuser()
        pid = os.getpid()
        pname = subprocess.Popen(["ps -o cmd= {}".format(pid)], stdout=subprocess.PIPE, shell=True)
        self.state_file = ("/{0:s}_{1:s}_{2:s}.state").format(program, user, pname)

    def load_state(self):
        # file does not exist
        if not os.path.isfile(self.state_file):
            return None

        # file exists
        with open(self.state_file) as f:
            text = f.read()
        return State(json.loads(text))

    def save_state(self, state):
        with open(self.state_file, 'w') as f:
            f.write(state.to_json())

    def remove_state_file(self):
        os.remove(self.state_file)

    def set_state(self, state):
        self.current_state = state

    def start(self):
        if self.current_state is None:
            raise NoStateException()

        while True:
            self.current_state.run()
            self.current_state = self.current_state.next_state()
            if self.current_state is None:
                break

    def __setattr__(self, k, v):
        # on state change save
        if k == 'current_state':
            self.save_state(v)

        # Normal
        self.__dict__[k] = v
