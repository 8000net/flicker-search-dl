import os
import sys
import xml.etree.ElementTree as ET

import requests

API_KEY = ''
URL = 'https://api.flickr.com/services/rest/'
METHOD = 'flickr.photos.search'

def download_photo(farm, server, id, secret):
    """
    Return bytes array of photo
    """
    url = 'https://farm%s.staticflickr.com/%s/%s_%s_m.jpg' % (
            farm, server, id, secret)
    r = requests.get(url)
    return r.content

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

    hashes = set()
    photo_num = 0
    page = 1
    while num_photos > 0:
        if num_photos < 100:
            params['per_page'] = num_photos
        params['page'] = page

        r = requests.get(URL, params=params)
        photos = ET.fromstring(r.text)[0]
        for photo in photos:
            attribs = extract_photo_attribs(photo)

            # Get image contents, check for duplicates
            image_data = download_photo(**attribs)
            hash_ = hash(image_data)
            if hash_ in hashes:
                continue
            hashes.add(hash_)

            # Save image to disk
            photo_dl_path = os.path.join(dl_path,
                    '%s_%d.jpg' % (file_tag, photo_num))
            with open(photo_dl_path, 'wb') as f:
                f.write(image_data)
            print('Downloaded %s_%d.jpg' % (file_tag, photo_num))
            photo_num += 1

        page += 1
        num_photos -= 100


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage: %s: ' % sys.argv[0] + \
              '<search text> <file tag> <download path> <# of photos>')
        exit(1)

    text = sys.argv[1]
    file_tag = sys.argv[2]
    dl_path = sys.argv[3]
    num_photos = int(sys.argv[4])

    download_by_text(text, file_tag, dl_path, num_photos)
