import signal
import time


class Timeout(Exception):
    pass


def try_one(func, t):
    #def timeout_handler(signum, frame):
    def timeout_handler():
        raise Timeout()

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(t)  # trigger alarm in 3 seconds

    try:
        #t1 = time.clock()
        return func()
        #t2 = time.clock()

    except Timeout:
        print('{} timed out after {} seconds'.format(func.__name__, t))
        return None
    finally:
        signal.signal(signal.SIGALRM, old_handler)

    #signal.alarm(0)
    #return t2-t1


try_one(60, f)
