class Unit:
    def __init__(self, value, unit):
        self.base_value = value * unit

    def to(self, unit):
        return self.base_value / unit

    def __add__(self, other):
        return Unit(self.base_value + other.base_value, 1)

    def __sub__(self, other):
        return Unit(self.base_value - other.base_value, 1)

    def __mul__(self, other):
        return Unit(self.base_value * other.base_value, 1)

    def __truediv__(self, other):
        return Unit(self.base_value / other.base_value, 1)

    def __iadd__(self, other):
        return Unit(self.base_value + other.base_value, 1)

    def __isub__(self, other):
        return Unit(self.base_value - other.base_value, 1)

    def __imul__(self, other):
        return Unit(self.base_value * other.base_value, 1)

    def __itruediv__(self, other):
        return Unit(self.base_value / other.base_value)

    def __neg__(self):
        return Unit(-1 * self.base_value, 1)

    def __pos__(self):
        return Unit(self.base_value, 1)

    def __abs__(self):
        return Unit(abs(self.base_value), 1)

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


class Constant(Unit):
    def __init__(self, value):
        Unit.__init__(self, value, 1.0)


class Length(Unit):
    def __init__(self, value, unit):
        Unit.__init__(value, unit)
    m = 1.0
    mm = m * .001
    cm = m * .01
    km = m * 1000.0

    inch = 0.0254
    ft = inch * 12.0


class Angular(Unit):
    def __init__(self, value, unit):
        Unit.__init__(value, unit)
    degree = 1.0
    radian = degree * 0.0174533
    rev = degree / 360.0


class Time(Unit):
    def __init__(self, value, unit):
        Unit.__init__(value, unit)
    s = 1.0
    ms = s * .001
    minute = s * 60.0
    hr = minute * 60.0


class Velocity(Unit):
    def __init__(self, value, unit):
        Unit.__init__(value, unit)
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
    def __init__(self, value, unit):
        Unit.__init__(value, unit)
    rpm = Angular.rev / Time.s
    rps = Angular.rev / Time.s
    rad_s = Angular.radian / Time.s
    deg_s = Angular.degree / Time.s


class Acceleration(Unit):
    def __init__(self, value, unit):
        Unit.__init__(value, unit)
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
    def __init__(self, value, unit):
        Unit.__init__(value, unit)
    N = 1
    oz = 3.59694309
    lbs = 0.224808942443
