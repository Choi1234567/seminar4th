from abc import ABCMeta


class BoundedMeta(type):
    _counter = {}
    _max_instance_count = None

    def __new__(mcs, name, bases, dict_data, max_instance_count):
        mcs._counter[name] = 0
        mcs._max_instance_count = max_instance_count
        return super().__new__(mcs, name, bases, dict_data)

    def __call__(cls, *args, **kwargs):
        cls._counter[cls.__name__] += 1
        if cls._max_instance_count is not None and cls._counter[cls.__name__] > cls._max_instance_count:
            raise TypeError
        else:
            return super().__call__(*args, **kwargs)


class BoundedBase(metaclass=ABCMeta):
    _max_instance_count = None
    _counter = {}

    @classmethod
    def get_max_instance_count(cls):
        pass

    def __init__(self):
        if self._counter.get(self.__class__.__name__, 0) == 0:
            self._counter[self.__class__.__name__] = 0
        self._counter[self.__class__.__name__] += 1
        max_instance_count = self.get_max_instance_count()
        if max_instance_count is not None and self._counter[self.__class__.__name__] > max_instance_count:
            raise TypeError

    pass


class tracer:
    def __init__(self, func):
        self.calls = 0
        self.func = func

    def __call__(self, *args, **keys):
        self.calls += 1
        return self.calls


@tracer
def smart_function():
    pass

if __name__ == '__main__':
    class C(metaclass=BoundedMeta, max_instance_count=2):
        pass


    c1 = C()
    c2 = C()
    try:
        c3 = C()
    except TypeError:
        print('everything works fine !')
    else:
        print('something goes wrong !')


    class D(BoundedBase):
        @classmethod
        def get_max_instance_count(cls):
            return 1


    d1 = D()
    try:
        d2 = D()
    except TypeError:
        print('everything works fine !')
    else:
        print('something goes wrong !')

    for real_call_count in range(1, 5):
        assert smart_function() == real_call_count
