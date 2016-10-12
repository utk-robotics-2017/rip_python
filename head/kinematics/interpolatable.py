class InterpolatingMap:
    def __init__(self, size):
        self.size = size
        self.key_list = []
        self.d = {}

    def put(self, key, value):
        self.d[key] = value
        self.key_list.append(key)

        def get_value(item):
            return self.d[item].value

        self.key_list.sort(key=get_value)
        if(len(self.d) > self.size):
            del self.d[self.key_list[0]]
            self.key_list = self.key_list[1:]

    def get(self, key):
        if key in self.d:
            return self.d[key]
        else:
            # Get surrounding keys for interpolation
            top_bound = None
            bottom_bound = None
            if key <= self.key_list[0]:
                top_bound = self.key_list[0]
            elif key >= self.key_list[-1]:
                bottom_bound = self.key_list[-1]
            else:
                for i in range(len(self.key_list)):
                    if self.key_list[i] > key and i > 0:
                        bottom_bound = self.key_list[i - 1]
                        top_bound = self.key_list[i]
                        break

            '''
                If attempting interpolation at ends of tree, return the nearest
                data point
            '''
            if top_bound is None and bottom_bound is None:
                return
            elif top_bound is None:
                return self.d[bottom_bound]
            elif bottom_bound is None:
                return self.d[top_bound]
            else:
                return self.d[bottom_bound].interpolate(self.d[top_bound],
                                                        bottom_bound.inverse_interpolate(top_bound, key))


class InterpolatingDouble:
    def __init__(self, value):
        self.value = value

    def interpolate(self, other, x):
        dydx = other.value - self.value
        searchY = dydx * x + self.value
        return InterpolatingDouble(searchY)

    def inverse_interpolate(self, upper, query):
        upper_to_lower = upper.value - self.value
        if upper_to_lower <= 0:
            return 0
        query_to_lower = query.value - self.value
        if query_to_lower <= 0:
            return 0
        return query_to_lower / upper_to_lower

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def get_value(self):
        return self.value
