#!/usr/bin/env python3
#
# an fdroid plugin to do `fdroid update` while using apps from repos
#
# This inserts itself into the `fdroid update` process to build repo
# based on the contents of other repos.  The chosen apps are specified
# by adding a standard fdroid metadata file for each app.  This
# metadata file only needs to have the fields that should override the
# metadata from the upstream repo.  This will then download all
# metadata, APKs, and graphics and include it in this repo.
#
# Categories and AntiFeatures are special cases.  The contents are
# merged with the contents from the upstream repo.  This lets this
# repo add Categories and AntiFeatures while still keeping the
# upstream ones.
#
#
# TODO only include Orbot arm64-v8a APKs
# TODO this should include AllowedAPKSigningKeys from the git metadata file

import json
import os
from datetime import datetime
from fdroidserver import index, metadata, mirror, update
from urllib.parse import urlsplit, urlunsplit

fdroid_summary = 'download all updates from repos, then run `fdroid update`'


# order by highest priority first
SOURCE_REPOS = [
    'https://briarproject.org/fdroid/repo?fingerprint=1FB874BEE7276D28ECB2C9B06E8A122EC4BCB4008161436CE474C257CBF49BD6',
    'https://guardianproject.info/fdroid/repo?fingerprint=B7C2EEFD8DAC7806AF67DFCD92EB18126BC08312A7F2D6F3862E46013C7A6135',
    'https://f-droid.org/repo?fingerprint=43238D512C1E5EB2D6569F4A3AFBF5523418B82E0A3ED1552770ABB9A9C9CCAB',
]


def get_cache():
    cache_file = os.path.join('tmp', os.path.basename(__file__) + '-cache.json')
    cache = None
    if os.path.exists(cache_file):
        try:
            with open(cache_file) as fp:
                cache = json.load(fp)
            if sorted(SOURCE_REPOS) == sorted(cache['etags'].keys()):
                print('Loading indexes from cache')
            else:
                print('Reseting cache')
                cache = None
        except Exception as e:
            print(e)
    if not cache:
        cache = {'etags': {}, 'indexes': {}}

    for url in SOURCE_REPOS:
        print(url)
        etags = cache['etags']
        data, etag = index.download_repo_index(url, etags.get(url))
        if data is None:
            data = cache['indexes'].get(url)
        cache['indexes'][url] = data
        if data is not None and etag != etags.get(url):
            etags[url] = etag
            with open(cache_file, 'w') as fp:
                json.dump(cache, fp, indent=2, sort_keys=True)
    return cache


def download_graphics(repourl, app):
    baseurl = urlsplit(repourl)
    for locale, entries in app.get('localized', {}).items():
        for k, v in entries.items():
            dirpath = None
            dlurl = None
            if k in ('icon', 'featureGraphic'):
                dirpath = os.path.join(
                    app['packageName'], locale, k + v[v.rindex('.') :]
                )
                dlpath = os.path.join('metadata', dirpath)
                dlurl = urlunsplit(
                    [
                        baseurl.scheme,
                        baseurl.netloc,
                        os.path.join(baseurl.path, dirpath),
                        None,
                        None,
                    ]
                )
                if not os.path.exists(dlpath):
                    print('Downloading', dlurl)
                    os.makedirs(os.path.dirname(dlpath), exist_ok=True)
                    net.download_file(dlurl, dlpath)
            elif k.endswith('Screenshots'):
                for f in v:
                    dirpath = os.path.join(app['packageName'], locale, k, f)
                    dlpath = os.path.join('repo', dirpath)
                    dlurl = urlunsplit(
                        [
                            baseurl.scheme,
                            baseurl.netloc,
                            os.path.join(baseurl.path, dirpath),
                            None,
                            None,
                        ]
                    )
                    if not os.path.exists(dlpath):
                        print('Downloading', dlurl)
                        os.makedirs(os.path.dirname(dlpath), exist_ok=True)
                        net.download_file(dlurl, dlpath)
            elif k in ('summary', 'description'):
                f = os.path.join('metadata', app['packageName'], locale, k + '.txt')
                os.makedirs(os.path.dirname(f), exist_ok=True)
                with open(f, 'w') as fp:
                    fp.write(v)
            elif k == 'whatsNew':
                f = os.path.join(
                    'metadata',
                    app['packageName'],
                    locale,
                    'changelogs',
                    '{}.txt'.format(app['suggestedVersionCode']),
                )
                os.makedirs(os.path.dirname(f), exist_ok=True)
                with open(f, 'w') as fp:
                    fp.write(v)


def read_metadata_ersatz():
    print('read_metadata_ersatz')

    # wget will preserve the file date when downloading, so use that date in the index
    update.options.use_date_from_apk = True

    urls = []
    find_repo = dict()
    apps_from_repo = dict()
    cache = get_cache()
    apps = real_read_metadata()

    for appid in apps.keys():
        found = False
        for url in SOURCE_REPOS:
            data = cache['indexes'][url]
            for app in data['apps']:
                if appid == app['packageName']:
                    from_metadata = apps[appid]
                    newapp = dict()
                    for k, v in app.items():
                        # convert to field names used in metadata files
                        if k == 'added':
                            newapp[k] = datetime.fromtimestamp(int(v) / 1000)
                        else:
                            newapp[k[0].upper() + k[1:]] = v
                    for k, v in from_metadata.items():
                        if not newapp.get(k):
                            newapp[k] = v
                    categories = set(newapp.get('Categories', []))
                    categories.update(apps[appid].get('Categories', []))
                    newapp['Categories'] = sorted(categories)
                    print("newapp['Categories']", newapp['Categories'])
                    apps[appid] = metadata.App(newapp)

                    baseurl = urlsplit(url)
                    i = 0
                    for package in data['packages'].get(appid):
                        apkurl = urlunsplit(
                            [
                                baseurl.scheme,
                                baseurl.netloc,
                                os.path.join(baseurl.path, package['apkName']),
                                None,
                                None,
                            ]
                        )
                        urls.append(apkurl)
                        i += 1
                        if i >= update.config['archive_older']:
                            break
                    download_graphics(url, app)
                    found = True
                    break
            if found:
                break

    mirror.options = update.options
    mirror._run_wget('repo', urls)
    return apps


def main():
    global real_read_metadata
    real_read_metadata = metadata.read_metadata
    metadata.read_metadata = read_metadata_ersatz
    update.main()


if __name__ == "__main__":
    main()
