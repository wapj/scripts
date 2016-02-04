#!/bin/bash

echo "START REMOVE ANDROID"

# remove android studio
rm -Rf /Applications/Android\ Studio.app
rm -Rf ~/Library/Preferences/AndroidStudio*
rm ~/Library/Preferences/com.google.android.studio.plist
rm -Rf ~/Library/Application\ Support/AndroidStudio*
rm -Rf ~/Library/Logs/AndroidStudio*
rm -Rf ~/Library/Caches/AndroidStudio*

# AndroidStudio projects
rm -Rf ~/AndroidStudioProjects

# android
rm -Rf ~/.android

# gradle
rm -Rf ~/.gradle

# remove andoid sdk
rm -Rf ~/Library/Android*


echo "DONE"
