import time

from .component import Component


class Motor(Component):
    DRIVE = "kDriveMotor"
    STOP = "kStopMotor"

    def __init__(self, spine, devname, config, commands, sim):
        self.spine = spine
        self.devname = devname
        self.label = config['label']
        self.index = config['index']
        self.sim = sim

        if sim:
            from ...simulator.sim_motor import *
            if config['type'].lower() == "Vex393":
                self.sim_motor = Vex393()
            self.sim_value = 0
            self.sim_velocity = 0
        else:
            self.driveIndex = commands[self.DRIVE]
            self.stopIndex = commands[self.STOP]

    def get_command_parameters(self):
        yield self.driveIndex, [self.DRIVE, "ii"]
        yield self.stopIndex, [self.STOP, "i"]

    def drive(self, value):
        if self.sim:
            self.sim_value = value
            self.sim_velocity = self.sim_motor.get_velocity(value)
            return

        if value == 0:
            self.stop()
            return
        self.spine.send(self.devname, False, self.DRIVE, self.index, value)

    def stop(self):
        if self.sim:
            self.sim_value = 0
            self.sim_velocity = 0
            return

        self.spine.send(self.devname, False, self.STOP, self.index)

    def pid_set(self, value):
        self.drive(value)

    def run_tests(self):
        run_again = True
        while run_again:
            print("Test 1: Driving {0:s} forwards".format(self.label))
            self.drive(500)
            time.sleep(2)
            self.stop()
            while True:
                ans = input("Would you like to run test 1 again? (y/n)\n")
                if ans.lower() in ['yes', 'y']:
                    break
                elif ans.lower() in ['no', 'n']:
                    run_again = False
                    break
                else:
                    print("Invalid response")
            while True:
                ans = input("Did test 1 pass? (y/n)\n")
                if ans.lower() in ['yes', 'y']:
                    break
                elif ans.lower() in ['no', 'n']:
                    return self.FAILED_TEST
                else:
                    print("Invalid response")

        run_again = True
        while run_again:
            print("Test 2: Driving {0:s} backwards".format(self.label))
            self.drive(-500)
            time.sleep(2)
            self.stop()
            while True:
                ans = input("Would you like to run test 2 again? (y/n)\n")
                if ans.lower() in ['yes', 'y']:
                    break
                elif ans.lower() in ['no', 'n']:
                    run_again = False
                    break
                else:
                    print("Invalid response")
            while True:
                ans = input("Did test 2 pass? (y/n)\n")
                if ans.lower() in ['yes', 'y']:
                    break
                elif ans.lower() in ['no', 'n']:
                    return self.FAILED_TEST
                    break
                else:
                    print("Invalid response")
        return self.PASSED_TEST

    def show_suggestions(self):
        print("If the motor drove in the wrong way then update your config")
        print("If the motor did not run at all then check your wiring")

    def sim_update(self, tm_diff):
        # TODO
        pass

    def get_hal_data(self):
        hal_data = {}
        hal_data['value'] = self.sim_value
        hal_data['velocity'] = self.sim_velocity
        return hal_data
