import os
import sys
from urllib.request import urlretrieve
import xml.etree.ElementTree as ET

import requests

API_KEY = ''
URL = 'https://api.flickr.com/services/rest/'
METHOD = 'flickr.photos.search'

def download_photo(farm, server, id, secret, dl_path):
    url = 'https://farm%s.staticflickr.com/%s/%s_%s_m.jpg' % (
            farm, server, id, secret)
    urlretrieve(url, dl_path)

def extract_photo_attribs(photo_element):
    keys = ['farm', 'server', 'id', 'secret']
    return {k: photo_element.attrib[k] for k in keys}

def download_by_text(text, file_tag, dl_path, num_photos):
    params = {
        'method': METHOD,
        'api_key': API_KEY,
        'text': text,
        'sort': 'relevance',
        'content_type': 1,           # photos only
        'media': 'photos',
        'page': 1
    }

    photo_num = 0
    page = 1
    while num_photos > 0:
        if num_photos < 100:
            params['per_page'] = num_photos
        params['page'] = page

        r = requests.get(URL, params=params)
        photos = ET.fromstring(r.text)[0]
        for photo in photos:
            photo_dl_path = os.path.join(dl_path,
                    '%s_%d.jpg' % (file_tag, photo_num))
            attribs = extract_photo_attribs(photo)
            print('Downloading %s_%d.jpg' % (file_tag, photo_num))
            download_photo(**attribs, dl_path=photo_dl_path)
            photo_num += 1

        page += 1
        num_photos -= 100


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: %s: <search text> <file tag> <download path> <# of photos>' % sys.argv[0])

    text = sys.argv[1]
    file_tag = sys.argv[2]
    dl_path = sys.argv[3]
    num_photos = int(sys.argv[4])

    download_by_text(text, file_tag, dl_path, num_photos)
