#!/usr/bin/env python
"""
This is a pice of sample code that uploads a file using the filestore in CKAN
and attatches it to a specified dataset.

This code is written by Anton Lundin <anton@dohi.se>
for the OpenUmea project, http://www.openumea.se/.
"""

API_URL = "http://openumea.se/api"
API_KEY = "XXXXXXXX-YYYY-ZZZZ-XXXXXXXXXXXXXXXXX"
DATASET = "dataset"
FORMAT_OVERRRIDE = "xml"

import urllib2
import sys
import os
import json
import datetime
import mimetypes
import uuid


def get_storage_auth_form(filename):
    """ Fetch auth information from ckan. """
    req = urllib2.Request(API_URL + "/storage/auth/form/" + filename,
                          headers={'Authorization': API_KEY})
    return json.loads(urllib2.urlopen(req).read())


def get_storage_metadata(filename):
    """ Fetch metadata about the file from ckan. """
    req = urllib2.Request(API_URL + "/storage/metadata/" + filename,
                          headers={'Authorization': API_KEY})
    return json.loads(urllib2.urlopen(req).read())


def register_resource(resource):
    """ Register the uploaded file as a resource in ckan. """
    req = urllib2.Request(API_URL + "/action/resource_create",
                          data=json.dumps(resource),
                          headers={
                              'Authorization': API_KEY,
                              'Content-Type': 'application/json'
                          })
    return json.loads(urllib2.urlopen(req).read())


def post_multipart(host, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    req = urllib2.Request(host, data=body,
                          headers={'Content-Type': content_type})
    urllib2.urlopen(req)


# maybe switch to something based on from poster.encode import multipart_encode
# this code is picked and adapted from:
# http://code.activestate.com/recipes/146306/
def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = str(uuid.uuid1())
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"'
                 % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def get_content_type(filename):
    """ Try to guess mime type of file """
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def upload_file(filename):
    """
    Construct a uniq filename to upload as.
    Fetch auth data to upload that file
    Construct a multipart/form-data payload with auth and the file
    Fetch what metadata the storage has about the file
    And register the file in ckan as a resource.
    """
    upload_filename = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") +\
        "/" + os.path.basename(filename)
    auth_data = get_storage_auth_form(upload_filename)

    # Convert EVERYTHING to str, so we can keep file-content as str.
    # if something is unicode, python tries to upgrade everything to unicode to
    # then encode everything back as $codec
    # we don't know encoding of file, and we shouldn't care!
    post_multipart(
        str(auth_data['action']),
        [(str(kv['name']), str(kv['value'])) for kv in auth_data['fields']],
        [("file", upload_filename, open(filename, 'rb').read())])

    file_metadata = get_storage_metadata(upload_filename)

    resource = {}
    resource["package_id"] = DATASET
    resource["name"] = upload_filename
    resource["size"] = file_metadata["_content_length"]
    resource["url"] = file_metadata["_location"]
    resource["hash"] = file_metadata["_checksum"]
    resource["format"] = FORMAT_OVERRRIDE
    resource["mimetype"] = get_content_type(filename)
    resource["resource_type"] = "file.upload"

    register_resource(resource)

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            upload_file(arg)
        else:
            print "I only can upload files, not things like: " + arg
