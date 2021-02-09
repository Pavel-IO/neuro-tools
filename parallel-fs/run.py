import threading
import sys
import time
import random
import queue as queue

import subjects_example as subject_mod
import recon


def process_freesurfer(subject):
    '''Implemented in recon.py'''
    return recon.recon_subject(subject)


def status():
    global solved
    solved += 1
    num = len(subjects)
    return 'Finished {} from {}, {:.2f} % done.'.format(solved, num, 100 * solved / num)


def log_and_print(message):
    if log_file is not None:
        with open(log_file, 'a') as fh:
            fh.write(message + '\n')
    print(message)


def log_process_start(subject, worker_name):
    start_time_string = time.asctime(time.localtime(time.time()))
    output = 'Started {}:\n'.format(subject[0])
    output += 'Worker {}, at {}.\n'.format(worker_name, start_time_string)
    log_and_print(output)


def log_process_end(subject, worker_name, state, ellapsed_time):
    end_time_string = time.asctime(time.localtime(time.time()))
    state = state and el_time > 600
    state_str = 'correctly' if state else 'erroneously'
    output = 'Worker {} ends analysing subject {} {} at {}.\n'.format(worker_name, subject[0], state_str, end_time_string)
    output += 'Elapsed time: {:.2f} s ({:.2f} hours).\n'.format(ellapsed_time, ellapsed_time/3600)
    output += status() + '\n'
    log_and_print(output)


def analyse_subject(subject, worker_name):
    log_process_start(subject, worker_name)
    start_time = time.time()
    state = process_freesurfer(subject)
    ellapsed_time = time.time()-start_time
    log_process_end(subject, worker_name, state, ellapsed_time)


def worker(name):
    log_and_print('Worker {} initialized.'.format(name))
    while True:
        subject = q.get()
        if subject is None:
            log_and_print('Worker {} ends processing.'.format(name))
            return
        analyse_subject(subject, name)
        q.task_done()


if __name__ == '__main__':
    log_file = 'fs_process_log__'+ time.strftime('%Y_%m_%d__%H_%M_%S') + '.txt'

    subjects = subject_mod.get_list()
    solved = 0

    num_worker_threads = 8  # user input
    q = queue.Queue()
    threads = []
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker, args=('t{}'.format(i),))
        t.start()
        threads.append(t)

    for item in subjects:
        q.put(item)

    # block until all tasks are done
    q.join()

    # stop workers
    for i in range(num_worker_threads):
        q.put(None)
    for t in threads:
        t.join()

    print('All jobs finished.')
