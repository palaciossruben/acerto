#!/usr/bin/python3

import inspect
import sys
import time
from datetime import datetime
from multiprocessing import Process

from context_search import run as context_search_run
from match.model import run as model_run
from search_engine import run as search_engine_run
from subscribe import helper as h
from subscribe.document_reader import run as document_reader_run

CHECKING_INTERVAL = 60  # check each minute


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


def run_watchdog(f, limit_hours=2.0):
    print("{}: STARTED {}".format(datetime.today(), retrieve_name(f)))

    start = time.time()
    p = Process(target=f, args=())
    p.start()

    while True:  # control cycle
        time.sleep(CHECKING_INTERVAL)
        if time.time() - start > limit_hours * 3600:
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
    #run_watchdog(document_reader_run, limit_hours=2)
    run_watchdog(search_engine_run, limit_hours=3)
    #run_watchdog(context_search_run, limit_hours=3)
    #run_watchdog(model_run, limit_hours=1)
    #run_watchdog(cluster_run, limit_hours=0.1)
    h.log('PROCESS MANAGER FINISHED')
