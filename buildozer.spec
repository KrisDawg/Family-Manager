# buildozer.spec for Family Manager Mobile App

[app]

# (str) Title of your application
title = Family Household Manager

# (str) Package name
package.name = com.familyhousehold.manager

# (str) Package domain (needed for android/ios packaging)
package.domain = org.familyhousehold

# (str) Source code where main.py lives
source.dir = .

# (list) Source files to include (let Kivy autodetect for now)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0.1

# (str) Application versioning (method 2)
version.code = 20260130

# (str) Application versioning (method 2)
# version.regex = __version__ = '(.*)'
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = sqlite3,kivy

# (list) Garden requirements
# garden_requirements =

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (str) Author of the application
author = Family Manager Team

# (str) Author email
author.email = contact@familyhouseholdmanager.com

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
# android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21

# (str) Android Build Tools version to use
android.build_tools = 33.0.2

# (bool) Use --private data storage (True) or --dir public storage (False)
# android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
# android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
# android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
# android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for continuous integration environments
# that need to build many applications.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
# android.whitelist =

# (str) Path to a custom whitelist file
# android.whitelist_src =

# (str) Path to a custom blacklist file
# android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
# android.add_jar =

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
# android.add_src =

# (list) Android AAR archives to add (same as add_jar, but should be AAR archives)
# android.add_aar =

# (list) Gradle dependencies to add (same format as requirements)
# android.gradle_dependencies =

# (list) Java classes to add as activities to the manifest
# android.add_activites =

# (str) python-for-android branch to use, defaults to master
# p4a.branch = master

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
# android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
# android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
# android.manifest.intent_filters =

# (str) launchMode to set for the main activity
# android.manifest.launch_mode = standard

# (str) screenOrientation to set for the main activity
# android.manifest.orientation = portrait

# (list) Android additional libraries to copy into libs/armeabi
# android.add_libs_armeabi = libs/android/*.so
# android.add_libs_armeabi_v7a = libs/android/*.so
# android.add_libs_arm64_v8a = libs/android/*.so
# android.add_libs_x86 = libs/android/*.so
# android.add_libs_mips = libs/android/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
# android.wakelock = False

# (list) Android application meta-data to set (key=value format)
# android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
# android.library_references =

# (list) Android shared libraries which will be added to AndroidManifest.xml using <uses-library> tags (NOT used by python-for-android)
# android.uses_library =

# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
# android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (int) overrides automatic versionCode computation (used in build.gradle)
# build incrementing version code each time in build.gradle
# android.numeric_version = 1

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup rules (see official auto backup documentation)
# android.backup_rules =

# (str) Android keystore for signing
android.keystore = %(source.dir)s/release.keystore
android.keystore.password = FamilyManager2026Secure!
android.alias = family-manager-release
android.alias.password = FamilyManager2026Secure!

# (str) If you need to insert variables into your AndroidManifest.xml file,
# override this kwarg_processor with a dict, it will be passed to the
# KwargsProcessor instance.
# android.manifest_kwargs = {}

# (str) If you need to insert variables into the gradle build file,
# override this kwarg_processor with a dict, it will be passed to the
# KwargsProcessor instance.
# android.gradle_kwargs = {}

#
# Python for android (p4a) specific
#

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
# p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
# p4a.local_recipes =

# (str) Filename to the hook for p4a
# p4a.hook =

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
# p4a.port =

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
# ios.kivy_ios_dir =
# Alternately, specify the directory in a custom build of kivy-ios, according to the instructions here:
# https://github.com/kivy/kivy-ios#custom-build-environment-variables
# ios.kivy_ios_dir = ../kivy-ios

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
# ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
# ios.codesign.release = "iPhone Distribution: <company name>"

#
# OSX Specific
#

# (str) Name of the certificate to use for signing the debug version
# osx.codesign.debug = "%(osx.codesign.common)s"

# (str) Name of the certificate to use for signing the release version
# osx.codesign.release = "%(osx.codesign.common)s"

#
# Web specific
#

# (str) Name of the certificate to use for signing the debug version
# web.codesign.debug = "%(web.codesign.common)s"

# (str) Name of the certificate to use for signing the release version
# web.codesign.release = "%(web.codesign.common)s"