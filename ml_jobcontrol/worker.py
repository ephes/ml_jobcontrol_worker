# -*- encoding: utf-8 -*-

import os
import json
import logging
import requests

from pprint import pprint
from urlparse import urljoin, urlparse

from .exceptions import MLJobControlException

logger = logging.getLogger(__name__)


class MLJobsUrls(dict):
    def __init__(self, urls):
        self.__dict__ = urls

    def __repr__(self):
        return repr(self.__dict__)


class MLJob(object):
    def __init__(self, job, local_path):
        # main attributes
        self.local_path = local_path
        self.train_num = job["classification_testset"]["train_num"]
        self.test_num = job["classification_testset"]["test_num"]
        self.url = job["url"]
        self.model_import_path = job["model_config"]["mlmodel"]["import_path"]
        self.model_config = json.loads(job["model_config"]["json_config"])
        self.model_args = self.model_config["args"]
        self.model_kwargs = self.model_config["kwargs"]

        # urls for put/patch requests
        self.testset_url = job["mlclassification_testset"]
        self.model_config_url = job["mlmodel_config"]

        # extract path information
        testset = job["classification_testset"]
        dataset = testset["mldataset"]
        datasets_path = os.path.join(self.local_path, "datasets")
        self.dataset_path = os.path.join(datasets_path, dataset["name"])
        filename = os.path.basename(urlparse(dataset["data_url"]).path)
        self.data_path = os.path.join(self.dataset_path, filename)

    def get_patch_payload(self):
        payload = {
            "mlclassification_testset": self.testset_url,
            "mlmodel_config": self.model_config_url
        }
        return payload

    def fetch_dataset(self):
        if os.path.exists(self.data_path):
            # use cached data
            return True
        else:
            # fetch data
            if not os.path.exists(self.dataset_path):
                os.makedirs(self.dataset_path)

            # fetch potentially large file (without using main memory)
            r = requests.get(dataset["data_url"], stream=True)
            if r.status_code == requests.codes.ok:
                with open(self.data_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                return True
        return False


class MLJobsWorker(object):
    def __init__(self, base_url, user, password, local_path):
        self.local_path = local_path
        self.session = requests.Session()
        self.fetch_urls(base_url)
        self.fetch_scores()
        self.login(user, password)

    def fetch_urls(self, base_url):
        r = self.session.get(base_url)
        self.base_url = base_url
        self.urls = MLJobsUrls(r.json())
        self.urls.login = urljoin(base_url, "api-auth/login/")
        self.urls.logout = urljoin(base_url, "api-auth/logout/")

    def fetch_scores(self):
        self.scores = {}
        r = self.session.get(self.urls.mlscore)
        if r.status_code == requests.codes.ok:
            for score in r.json():
                self.scores[score["name"]] = score["url"]

    def create_score(self, score):
        payload = {"name": score}
        r = self.session.post(self.urls.mlscore, data=payload)
        if r.status_code == requests.codes.created:
            score = r.json()
            self.scores[score["name"]] = score["url"]
            return score["url"]
        else:
            msg = "could not create score: %s" % score
            logger.error(msg)
            raise MLJobControlException(msg)

    def login(self, user, password):
        payload = {
            'username': user,
            'password': password,
            'next': urlparse(self.base_url).path
        }
        r = self.session.post(self.urls.login, data=payload)
        if r.status_code == requests.codes.ok:
            # set json headers after login or else auth
            # would return 200 but still won't work o_O
            self.session.headers.update({
                'Content-type': 'application/json',
                'Accept': 'application/json',
            })
        else:
            msg = "could not log in"
            logger.error(msg)
            raise MLJobControlException(msg)

    def get_jobs_todo(self):
        payload = {'status': 'todo'}
        r = self.session.get(self.urls.mljobs, params=payload)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            logger.error("could not get todo jobs")
        return None

    def mark_job(self, job, status):
        payload = job.get_patch_payload()
        payload["status"] = status
        r = self.session.patch(job.url, data=json.dumps(payload))
        return r.status_code == requests.codes.ok

    def next_job(self):
        jobs_todo = self.get_jobs_todo()
        if jobs_todo is not None and len(jobs_todo) > 0:
            next_job = MLJob(jobs_todo[0], self.local_path)
            if self.mark_job(next_job, "in_progress"):
                if next_job.fetch_dataset():
                    return next_job
                else:
                    logger.error("could not fetch data: %s" % next_job.data_url)
            else:
                logger.error("couldn't set job status to 'in_progress'")
        else:
            logger.info("nothing to do")
        return None

    def submit_result(self, job, result):
        payload = []
        for k, v in result.iteritems():
            mlscore_url = self.scores.get(k)
            if mlscore_url is None:
                mlscore_url = self.create_score(k)
            payload.append({
                "mljob": job.url,
                "mlscore": mlscore_url,
                "score": v,
            })
        payload = json.dumps(payload)
        r = self.session.post(self.urls.mlresultscores,
            data=payload)
        if r.status_code == requests.codes.created:
            if not self.mark_job(job, "done"):
                logger.error("couldn't set job status to 'done'")
        else:
            msg = "could not submit results for: %s" % job.url
            logger.error(msg)
            raise MLJobControlException(msg)
