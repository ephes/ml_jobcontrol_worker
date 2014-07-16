# -*- encoding: utf-8 -*-

import argparse

from ml_jobcontrol import Worker

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="run tests against given url")
    parser.add_argument("user", help="login with this user")
    parser.add_argument("password", help="login with this password")
    parser.add_argument("datadir", help="use this dir to store data")
    args = parser.parse_args()

    worker = Worker(args.url, args.user, args.password,
        args.datadir)
    job = worker.next_job()
    result = {
        "f1": 0.666,
        "precision": 0.666,
        "recall": 0.666,
        "blubber": 0.5,
    }
    worker.submit_result(job, result)

if __name__ == '__main__':
    main()
