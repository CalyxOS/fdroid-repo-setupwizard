#!/usr/bin/env python3

import glob
import os

ANDROID_MK_HEADER = """# Auto generated, do not edit.
# see {file}

LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := F-Droid
LOCAL_SRC_FILES := F-Droid.apk
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_MODULE_CLASS := APPS
LOCAL_PRODUCT_MODULE := true
include $(BUILD_PREBUILT)

include $(CLEAR_VARS)
LOCAL_MODULE := fdroid-repo
LOCAL_MODULE_CLASS := ETC
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_PATH := $(TARGET_OUT_PRODUCT_ETC)/org.fdroid.fdroid
LOCAL_MODULE_STEM := additional_repos.xml
LOCAL_SRC_FILES := additional_repos.xml
LOCAL_PRODUCT_MODULE := true
include $(BUILD_PREBUILT)
"""

ANDROID_MK_APP = """
include $(CLEAR_VARS)
LOCAL_MODULE := {appid}
LOCAL_SRC_FILES := repo/$(LOCAL_MODULE).apk
LOCAL_MODULE_PATH := $(PRODUCT_OUT)/$(TARGET_COPY_OUT_PRODUCT)/fdroid/repo
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_MODULE_CLASS := APPS
LOCAL_DEX_PREOPT := false
LOCAL_NO_STANDARD_LIBRARIES := true
LOCAL_REPLACE_PREBUILT_APK_INSTALLED := $(LOCAL_PATH)/repo/$(LOCAL_MODULE).apk
include $(BUILD_PREBUILT)
"""

appids = []

with open('Android.mk', 'w') as fp:
    fp.write(ANDROID_MK_HEADER.format(file=__file__))
    for apk in sorted(glob.glob('repo/*.apk')):
        appid = os.path.basename(apk)[:-4]
        appids.append(appid)
        fp.write(ANDROID_MK_APP.format(appid=appid))


FDROID_REPO_MK_HEADER = """# Auto generated, do not edit.
# see {file}

PRODUCT_COPY_FILES += \\
    prebuilts/calyx/fdroid/fallback-icon.png:$(TARGET_COPY_OUT_PRODUCT)/fdroid/repo/fallback-icon.png \\
"""

FDROID_REPO_MK_LINE = """    prebuilts/calyx/fdroid/{path}:$(TARGET_COPY_OUT_PRODUCT)/fdroid/{path} \\
"""


with open('fdroid-repo.mk', 'w') as fp:
    fp.write(FDROID_REPO_MK_HEADER.format(file=__file__))
    paths = []
    for root, dirs, files in os.walk('repo'):
        for f in sorted(files):
            if not f.endswith('.apk'):
                paths.append(os.path.join(root, f))
    for path in sorted(paths):
        fp.write(FDROID_REPO_MK_LINE.format(path=path))
    fp.write("PRODUCT_PACKAGES += \\\n    fdroid-repo \\\n")
    for appid in appids:
        fp.write("    {appid} \\\n".format(appid=appid))
