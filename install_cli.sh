#`  ! /bin/bash 

# Location of lockin settings file
SETTINGS_FILE="src/lockin/settings.py"

#User input
read -p "Please enter your name: " HOST_NAME
clear
read -r -p "Please enter network shared folder location. Example: /Volumes/NAS/. Press enter to skip. \n" NETWORK_SHARE

if [$NETWORK_SHARE = '']
    NETWORK_SHARE = "/Volumes/NAS"
    echo 'Using defualt net work volume /Volumes/NAS'
fi

# Target strings to up date in settings file
HOST_TARGET_KEY="HOST"
NET_SHARE_TARGET_KEY="NETWORK_SHARE_URI"

# Replace strings in settings file
sed -i -e "s|\($HOST_TARGET_KEY *= *\).*|\1'$HOST_NAME'|" $SETTINGS_FILE
sed -i -e "s|\($NET_SHARE_TARGET_KEY *= *\).*|\1'$NETWORK_SHARE'|" $SETTINGS_FILE

# Ensure python3.10 is install and linked
echo "Cheking for python 3.10"
brew install python@3.10

# If virtualenv not installed, download & install it for user
if ! python3 -c "import virtualenv" &> /dev/null; then
    python3 -m pip install --user virtualenv
fi

mkdir ~/.lockin
cp lockin.sh requirements-cli.txt src/lockin/__init__.py src/lockin/cli.py src/lockin/manager.py src/lockin/cli_styles.py src/lockin/exceptions.py src/lockin/settings.py src/lockin/models.py ~/.lockin
cd ~/.lockin


# Create  virtual env and install dependencies
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements-cli.txt

# Make scirpt executable
chmod +x lockin.sh

# Link lockin command to lauch scirpt
sudo ln -fs ~/.lockin/lockin.sh /usr/local/bin/lockin