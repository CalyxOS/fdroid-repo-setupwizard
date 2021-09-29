#!/usr/bin/env python3
#
# Download the most recent Signal APK if there is a newer release
# available.  This script is designed to be run frequently in a cron
# job, even as often as once a minute.

import hashlib
import json
import os
import requests
from pprint import pprint


# use generic User Agent to avoid being targetted
HEADERS = {'User-Agent': 'Wget/1.21.1'}


def download_file(url):
    # the stream=True parameter keeps memory usage low
    r = requests.get(url, stream=True, allow_redirects=True, headers=HEADERS)
    r.raise_for_status()
    os.makedirs('tmp', exist_ok=True)
    h = hashlib.sha256()
    f = os.path.join('tmp', os.path.basename(url))
    with open(f, 'wb') as fp:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                fp.write(chunk)
                h.update(chunk)
    return f, h.hexdigest()


def main():
    url = 'https://updates.signal.org/android/latest.json'
    r = requests.get(url, allow_redirects=True, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    apkfile = 'repo/org.thoughtcrime.securesms_%s.apk' % data['versionCode']

    if not os.path.exists(apkfile):
        print(apkfile, 'does not exist, downloading')
        f, sha256 = download_file(data['url'])
        if data['sha256sum'] != sha256:
            print('ERROR', f, 'SHA-256', sha256, 'does not match:')
            print(json.dumps(data, indent=2, sort_keys=True))
            exit(1)
        os.link(f, apkfile)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main()
