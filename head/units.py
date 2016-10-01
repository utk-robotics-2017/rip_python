class Unit:
    def __init__(self, value, unit):
        self.base_value = value * unit

    def to(self, unit):
        return self.base_value / unit

    def __add__(self, other):
        return Unit(self.base_value + other.base_value, 1)

    def __sub__(self, other):
        return Unit(self.base_value - other.base_value, 1)

    def __mult__(self, other):
        return Unit(self.base_value * other.base_value, 1)

    def __truediv__(self, other):
        return Unit(self.base_value / other.base_value, 1)

    def __iadd__(self, other):
        self.base_value += other.base_value

    def __isub__(self, other):
        self.base_value -= other.base_value

    def __imult__(self, other):
        self.base_value *= other.base_value

    def __itruediv__(self, other):
        self.base_value /= other.base_value

    def __neg__(self):
        self.base_value *= -1

    def __pos__(self):
        pass

    def __abs__(self):
        self.base_value = abs(self.base_value)

    def __lt__(self, other):
        return self.base_value < other.base_value

    def __le__(self, other):
        return self.base_value <= other.base_value

    def __eq__(self, other):
        return self.base_value == other.base_value

    def __ne__(self, other):
        return self.base_value != other.base_value

    def __gt__(self, other):
        return self.base_value > other.base_value

    def __ge__(self, other):
        return self.base_value >= other.base_value


class Length(Unit):
    m = 1
    mm = m * .001
    cm = m * .01
    km = 1000 * m

    inch = 0.0254
    ft = inch * 12


class Angular(Unit):
    degree = 1
    radian = degree * 0.0174533
    rev = degree / 360


class Time(Unit):
    s = 1
    ms = s * .001
    minute = s * 60
    hr = minute * 60


class Velocity(Unit):
    m_s = Length.m / Time.s
    m_minute = Length.m / Time.minute

    mm_s = Length.mm / Time.s
    mm_minute = Length.mm / Time.minute

    cm_s = Length.cm / Time.s
    cm_minute = Length.cm / Time.minute

    inch_s = Length.inch / Time.s
    inch_minute = Length.inch / Time.minute

    ft_s = Length.ft / Time.s
    ft_minute = Length.ft / Time.minute


class AngularVelocity(Unit):
    rpm = Angular.rev / Time.s
    rps = Angular.rev / Time.s
    rad_s = Angular.radian / Time.s
    deg_s = Angular.degree / Time.s


class Acceleration(Unit):
    m_s2 = Length.m / Time.s ** 2
    m_minute2 = Length.m / Time.minute ** 2

    mm_s2 = Length.mm / Time.s ** 2
    mm_minute = Length.mm / Time.minute ** 2

    cm_s2 = Length.cm / Time.s ** 2
    cm_minute2 = Length.cm / Time.minute ** 2

    inch_s2 = Length.inch / Time.s ** 2
    inch_minute2 = Length.inch / Time.minute ** 2

    ft_s2 = Length.ft / Time.s ** 2
    ft_minute2 = Length.ft / Time.minute ** 2


class Force(Unit):
    N = 1
    oz = 3.59694309
    lbs = 0.224808942443
