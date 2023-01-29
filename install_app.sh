#! /bin/bash

#Welcome!
echo 'LockIn Installer'

# Location of lockin settings file
SETTINGS_FILE="src/lockin/settings.py"

#User input
read -p "Please enter your name: " HOST_NAME
read -r -p "Please enter network shared folder location. Example: /Volumes/NAS/. Press enter to skip. " NETWORK_SHARE

# Target strings to up date in settings file
HOST_TARGET_KEY="HOST"
NET_SHARE_TARGET_KEY="NETWORK_SHARE_URI"

# Replace strings in settings file
sed -i -e "s|\($HOST_TARGET_KEY *= *\).*|\1'$HOST_NAME'|" $SETTINGS_FILE
sed -i -e "s|\($NET_SHARE_TARGET_KEY *= *\).*|\1'$NETWORK_SHARE'|" $SETTINGS_FILE


# If virtualenv not installed, download & install it for user
if ! python3 -c "import virtualenv" &> /dev/null; then
    python3 -m pip install --user virtualenv
fi

# Create  virtual env and install dependencies
python3 -m virtualenv lockin_env
source lockin_env/bin/activate
pip install -r requirements.txt

# Install briefcase
pip install briefcase

# Build app template
briefcase build

# Package app template to build disk image
briefcase package --no-sign

# Open disk image to promp user and install
open macOS/LockIn-0.0.1.dmg
