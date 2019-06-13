import sys
import threading
import time


class KeyListener:

    @staticmethod
    def always_true():
        return True

    def __init__(self, dictionary, update_time, while_func=always_true):
        """

            calls given function when corresponding key is entered on console

        :param dictionary:  a python dictionary containing Tuples with a function and args as values
                            Bsp:    {"key":(func, arg1, arg2...),
                                    "key2":(func2, arg1, arg2...)}
        :param update_time: time between reads
        :param while_func:  function returning a boolean, stopping the  key checking Thread if True
                            default function returns always True
        """

        def _check_key():
            while while_func():
                input_key = sys.stdin.read(1)

                for key, funcTuple in dictionary.items():
                    if input_key is key:
                        funcTuple[0](*tuple(list(funcTuple)[1:]))
                time.sleep(update_time)

        threading.Thread(target=_check_key, daemon=True).start()
