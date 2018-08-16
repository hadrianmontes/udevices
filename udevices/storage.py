class Deque(list):
    def __init__(self, *args, max_len=20, **kwargs):
        self._max_len = max_len
        super(Deque, self).__init__(*args, **kwargs)
        self._check_size()

    def append(self, *args, **kwargs):
        super(Deque, self).append(*args, **kwargs)
        self._check_size()

    def _check_size(self):
        while len(self) > self._max_len:
            self.pop(0)



class MultipleHistorial(object):
    """Creates an object to store information about different Historic
    data saved with different frequencies.

    Parameters:
    -----------
    period_multipliers : list(int)
        List with integers determining with wich frecuency the data
        will be saved. i.e. a value of 2 means that the data is stored
        once every 2 measures.
    dimension : int (optional)
        Dimension of the data to be stored. Default 2
    *kwargs : keyword arguments for the Deque class
    """

    def __init__(self, period_multipliers, dimension=2, **kwargs):
        super(MultipleHistorial, self).__init__()
        self._historials = {}
        self._counters = {}
        self._dimension = dimension
        self._period_multipliers = list(sorted(period_multipliers))
        self.current = self._period_multipliers[0]

        
        for multiplier in self._period_multipliers:
            self._counters[multiplier] = multiplier
            self._historials[multiplier] = tuple(Deque()
                                                 for _ in range(dimension))

    def __getitem__(self, index):
        return self._historials[self.current][index]

    def __str__(self):
        return self._historials.__str__()

    def __repr__(self):
        return self._historials.__repr__()

    def add(self, values):
        """
        Adds the values to the historial records if it is time to update it.

        Parameters
        ----------
        values : list or tuple
            Iterable with the same length than the historial records.

        Raises
        ------
        ValueError : If the size of the list/tuple does not match the
                     record length
        """

        if len(values) != self._dimension:
            text = "Values with size {} do not match record length {}"
            text = text.format(len(values), self._dimension)
            raise ValueError(text)

        for multipler, counter in self._counters.items():
            if counter == multipler:
                self._counters[multipler] = 0
                for index, value in enumerate(values):
                    self._historials[counter][index].append(value)

            self._counters[multipler] += 1

    def cycle(self):
        """
        Changes the current historial to the next one
        """
        self._current = (self._current + 1) % len(self._period_multipliers)

    @property
    def current(self):
        """
        Current index for the get index method
        """
        return self._period_multipliers[self._current]
    @current.setter
    def current(self, value):
        self._current = self._period_multipliers.index(value)

    @property
    def dimension(self):
        """
        The dimension of the recod data
        """

        return self._dimension

    @property
    def fastest(self):
        """
        Returns the period of the fastest mode
        """
        return min(self._period_multipliers)

    @property
    def slowest(self):
        """
        Reruns the period of the slowest mode
        """
        return max(self._period_multipliers)
    
