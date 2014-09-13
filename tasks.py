from google.appengine.ext import deferred
from google.appengine.ext import blobstore


import imgur
from model import Dive, Tag


def upload_photo(blob_ids, dive_id):
    deferred.defer(_upload_photo,
                   blob_ids,
                   dive_id
                   )


def _upload_photo(blob_ids, dive_id):
    dive = Dive.get_by_id(int(dive_id))
    for blob_id in blob_ids:
        blob_info = blobstore.BlobInfo.get(blob_id)

        f = blob_info.open()
        img = f.read()
        f.close()

        if img is None:
            raise Exception("Invalid blob")
        links = imgur.upload_image(img)
        dive.add_photo(links)
        blobstore.delete(blob_id)
    dive.put()


def tag_dive(dive):
    deferred.defer(_tag_dive, dive)


def _tag_dive(dive):
    for t in dive.dive_data['tags']:
        if t == '--':
            continue
        Tag.add_dive(t, dive)
        print t
