# -*- encoding: utf-8 -*-

import argparse

from pprint import pprint

from ml_jobcontrol import Worker
from ml_jobcontrol.config import activate_logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="run tests against given url")
    parser.add_argument("token", help="authenticate with this token")
    parser.add_argument("datadir", help="use this dir to store data")
    args = parser.parse_args()

    worker = Worker(args.url, args.token, args.datadir)
    job = worker.next_job()
    if job is not None:
        pprint(job.model_import_path)
        pprint(job.model_config)
        pprint(job.model_args)
        pprint(job.model_kwargs)
        result = {
            "f1": 0.666,
            "precision": 0.666,
            "recall": 0.666,
            "blubber": 0.5,
        }
        worker.submit_result(job, result)

if __name__ == '__main__':
    main()
