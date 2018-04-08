#!/usr/bin/python3

import time
import sys
import inspect
from datetime import datetime
from multiprocessing import Process
from subscribe.document_reader import run as document_reader_run
from subscribe.search_engine import run as search_engine_run
from match.clustering import run as cluster_run
from context_search import run as context_search_run
from match.model import run as model_run
from subscribe import helper as h

CHECKING_INTERVAL = 60  # check each minute
LIMIT_TIME = 7200  # 1 hour

#CHECKING_INTERVAL = 1  # test, remove
#LIMIT_TIME = 10  # 1 test, remove


def retrieve_name(var):
        """
        Gets the name of var. Does it from the out most frame inner-wards.
        :param var: variable to get name from.
        :return: string
        """
        for fi in reversed(inspect.stack()):
            names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
            if len(names) > 0:
                return names[0]


def run_watchdog(f):
    print("{}: STARTED {}".format(datetime.today(), retrieve_name(f)))

    start = time.time()
    p = Process(target=f, args=())
    p.start()

    while True:  # control cycle
        time.sleep(CHECKING_INTERVAL)
        if time.time() - start > LIMIT_TIME:
            p.terminate()
            p.join()
            print("ERROR Timeout: Process manager killed {p} after {seconds} second\n".format(p=retrieve_name(f),
                                                                                              seconds=str(time.time() - start)))

        if not p.is_alive():
            h.log('{0}, took: {1}'.format(retrieve_name(f), time.time() - start))
            break


if __name__ == '__main__':
    sys.stdout = h.Unbuffered(open('main.log', 'a'))

    h.log('PROCESS MANAGER STARTED')
    #run_watchdog(cluster_run)
    run_watchdog(document_reader_run)
    run_watchdog(search_engine_run)
    run_watchdog(context_search_run)
    run_watchdog(model_run)
    h.log('PROCESS MANAGER FINISHED')
