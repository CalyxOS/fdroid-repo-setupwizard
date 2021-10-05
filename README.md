
CalyxOS's Recommended Apps
==========================

This is shipped with CalyxOS so that the Setup Wizard can setup the apps without
an internet connection.

Both this Gitlab repository and this unofficial F-Droid repository are not
affiliated to, nor have been authorized, sponsored or otherwise approved by the
app developers.


How does it work?
-----------------

This uses scripts to poll well known download links for the apps.  When there is
a new APK available, it downloads it and puts it into place for the next `fdroid
update` run.  This uses a custom version of `fdroid update` which can download
all information for an app if it is available in specified fdroid repo.  Here is how
to run that:

```console
$ cd fdroid-repo-setupwizard
$ PYTHONPATH=`pwd`/plugins fdroid ersatz-update --help
```


How to add new apps
-------------------

#### If the app is available in an F-Droid repo

* Add a [metadata file](https://f-droid.org/docs/Build_Metadata_Reference) named
  after the [Application ID](https://developer.android.com/studio/build/configure-app-module?hl=lt#set_the_application_id) of the app, e.g. _metadata/app.organicmaps.yml_.
* [Generate](https://f-droid.org/docs/Build_Metadata_Reference/#AllowedAPKSigningKeys) the `AllowedAPKSigningKeys:` entry and add it to the metadata file.
* Make sure that the app is available in the [repos included in the script](-/blob/master/plugins/fdroid_ersatz-update.py).


#### If the app provides a direct download link

* Add a [metadata file](https://f-droid.org/docs/Build_Metadata_Reference) named
  after the [Application ID]() of the app, e.g. _metadata/org.thoughtcrime.securesms.yml_.
* [Generate](https://f-droid.org/docs/Build_Metadata_Reference/#AllowedAPKSigningKeys) the `AllowedAPKSigningKeys:` entry and add it to the metadata file.
* Fill out all the relevant fields in the metadata file.
* Include translations in this git repo, e.g. _metadata/org.thoughtcrime.securesms/en_US/summary.txt_
* Include graphics in this git repo, e.g. _metadata/org.thoughtcrime.securesms/en_US/icon.png_


#### Its only available elsewhere

* Figure out how to do this safely and legally.
* It will probably follow the same pattern as "direct download link" above.



I propose using this as the layout for the repo URLs:

| slug | git project | canonical URL |
|------|-------------|---------------|
| common | | |

| setupwizard |
| android11 |
| android12 |
| $device  |
| 
