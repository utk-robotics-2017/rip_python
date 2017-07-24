class State:
	''' State interface

		Attributes
		----------
		name: str
			Name of the state
	'''

    def __init__(self, name: str):
    	'''
    		Parameters
    		----------
    		name: str
    			Name of the state
    	'''
        self.name = name

    def run(self):
        raise NotImplemented("State run not implemented")

    def next(self):
        raise NotImplemented("State next not implemented")

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__
