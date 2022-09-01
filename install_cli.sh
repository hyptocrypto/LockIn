#! /bin/zsh

# # Location of lockin settings file
# SETTINGS_FILE="src/lockin/settings.py"

# #User input
# read -p "Please enter your name: " HOST_NAME
# read -r -p "Please enter network shared folder location. Example: /Volumes/NAS/. Press enter to skip. " NETWORK_SHARE

# # Target strings to up date in settings file
# HOST_TARGET_KEY="HOST"
# NET_SHARE_TARGET_KEY="NETWORK_SHARE_URI"

# # Replace strings in settings file
# sed -i -e "s|\($HOST_TARGET_KEY *= *\).*|\1'$HOST_NAME'|" $SETTINGS_FILE
# sed -i -e "s|\($NET_SHARE_TARGET_KEY *= *\).*|\1'$NETWORK_SHARE'|" $SETTINGS_FILE

# brew install python@3.10
# # If virtualenv not installed, download & install it for user
# if ! python3 -c "import virtualenv" &> /dev/null; then
#     python3 -m pip install --user virtualenv
# fi

mkdir ~/.lockin
cp requirements-cli.txt src/lockin/cli.py src/lockin/manager.py src/lockin/styles.py src/lockin/exceptions.py src/lockin/settings.py src/lockin/models.py ~/.lockin
cd ~/.lockin


# Create  virtual env and install dependencies
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements-cli.txt

chmod +x cli.py

sudo ln -fs ~/.lockin/cli.py /usr/local/bin/lockin


