#!/usr/bin/env python
"""
This is a pice of sample code that uploads a file using the filestore in CKAN
and attatches it to a specified dataset.

This code is written by Anton Lundin <anton@dohi.se>
for the OpenUmea project, http://www.openumea.se/.
"""

# To communicate with ckan
API_URL = "http://openumea.se/api"
API_KEY = "XXXXXXXX-YYYY-ZZZZ-XXXXXXXXXXXXXXXXX"
# list or dataset
DATASET = "dataset"
RESOURCES_TO_KEEP = 3

import urllib2
import json
import datetime


def do_action(action, data):
    """ Preform a action via CKAN action api"""
    req = urllib2.Request(API_URL + "/action/" + action,
                          data=json.dumps(data),
                          headers={
                              'Authorization': API_KEY,
                              'Content-Type': 'application/json'
                          })
    return json.loads(urllib2.urlopen(req).read())


def clean(dataset):
    """
    1. fetch all resources in a dataset
    2. sort them by created
    3. delete all but the 3 newest
    """
    package = do_action("package_show", {"id": dataset})

    resources = []
    for res in package["result"]["resources"]:
        res["created"] = datetime.datetime.strptime(
            res["created"], "%Y-%m-%dT%H:%M:%S.%f")
        resources.append(res)

    resources = sorted(resources, key=lambda obj: obj["created"])

    #TODO: use this when 2.0 is deployed, 1.8 doesn't have it
    #for res in resources[-RESOURCES_TO_KEEP:]:
    #    do_action("resource_delete", {"id": res["id"]})

    resources = resources[-RESOURCES_TO_KEEP:]
    for res in resources:
        res["created"] = str(res["created"])

    do_action("package_update", {
        "id": dataset,
        "resources": resources,
    })


def main():
    """
    Clean a dataset, keep RESOURCES_TO_KEEP number of resources
    """
    if type(DATASET) is not list:
        datasets = [DATASET]
    else:
        datasets = DATASET

    for dataset in datasets:
        clean(dataset)


if __name__ == '__main__':
    main()
