import sys
import threading
import time


class KeyListener:

    @staticmethod
    def true_func():
        return True

    def __init__(self, dictionary, until=True, until_func=true_func):
        """

            calls given function when corresponding key is entered on console

        :param dictionary: a python dictionary containing Tuples with a function and args as values
                    {"key":(func, arg1, arg2...),
                    "key2":(func2, arg1, arg2...)}
        :param until: boolean flag stopping the  key checking Thread if True
        :param until_func: function returning a boolean, stopping the  key checking Thread if True
        """

        def _check_key():
            while until and until_func():
                input_key = sys.stdin.read(1)

                for key, funcTuple in dictionary.items():
                    if input_key is key:
                        funcTuple[0](*tuple(list(funcTuple)[1:]))
                time.sleep(0.1)

        threading.Thread(target=_check_key, daemon=True).start()
