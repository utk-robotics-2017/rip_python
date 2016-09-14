class Unit:
    def __init_(self, value, unit):
        self.base_value = value / unit

    def to(self, unit):
        return self.base_value * unit

class Length(Unit):
    m = 1
    mm = m * .001
    cm = m * .01
    km = 1000 * m

    inch = 39.3701
    ft = inch * 12

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

class Acceleration(Unit):
    m_s2 = Length.m / Time.s**2
    m_minute2 = Length.m / Time.minute**2

    mm_s2 = Length.mm / Time.s**2
    mm_minute = Length.mm / Time.minute**2

    cm_s2 = Length.cm / Time.s**2
    cm_minute2 = Length.cm / Time.minute**2

    inch_s2 = Length.inch / Time.s**2
    inch_minute2 = Length.inch / Time.minute**2

    ft_s2 = Length.ft / Time.s**2
    ft_minute2 = Length.ft / Time.minute**2


