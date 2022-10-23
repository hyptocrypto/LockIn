#`  ! /bin/bash 

function style_stdout () {
    echo -e "\033[0;32m $1 \033[0m"
}
# Location of lockin settings file
SETTINGS_FILE="src/lockin/settings.py"

#User input
read -p "Please enter your name: " HOST_NAME
read -p "Please enter sudo password: " PASSWORD
echo -e "\n" 

read -r -p "Please enter network share host location. Example: //guest:@192.168.1.69/NAS. Press enter to skip \n" NAS_HOST
echo -e "\n"
read -r -p "Please enter local net work share mount point. Example: /Volumes/NAS/. Press enter to skip. " NETWORK_SHARE

if [$NETWORK_SHARE = '']
    then
    NETWORK_SHARE = "/Volumes/NAS"
    echo 'Using defualt net work volume /Volumes/NAS'
fi
if [$NAS_HOST = '']
    then
    NAS_HOST = "//guest:@192.168.1.69/NAS"
    echo 'Using defualt net work volume //guest:@192.168.1.69/NAS'
fi

# Target strings to up date in settings file
PASSWWORD_KEY="PASSWORD"
HOST_TARGET_KEY="HOST"
NET_SHARE_TARGET_KEY="NETWORK_SHARE_URI"
NAS_HOST_KEY="NAS_HOST"

# Replace strings in settings file
sed -i -e "s|\($HOST_TARGET_KEY *= *\).*|\1'$HOST_NAME'|" $SETTINGS_FILE
sed -i -e "s|\($PASSWORD_KEY *= *\).*|\1'$PASSWORD'|" $SETTINGS_FILE
sed -i -e "s|\($NET_SHARE_TARGET_KEY *= *\).*|\1'$NETWORK_SHARE'|" $SETTINGS_FILE
sed -i -e "s|\($NAS_HOST_KEY *= *\).*|\1'$NAS_HOST'|" $SETTINGS_FILE

# Ensure python3.10 is install and linked
style_stdout "Cheking for python 3.10"
brew install python@3.10
brew link --force python@3.10

mkdir ~/.lockin
cp lockin.sh requirements-cli.txt src/lockin/__init__.py src/lockin/cli.py src/lockin/manager.py src/lockin/cli_styles.py src/lockin/exceptions.py src/lockin/settings.py src/lockin/models.py ~/.lockin
cd ~/.lockin


# If virtualenv not installed, download & install it for user
if ! python3.10 -c "import virtualenv" &> /dev/null; then
    python3.10 -m pip install --user virtualenv
fi

style_stdout "Building Lockin CLI"
# Create  virtual env and install dependencies
python3.10 -m virtualenv ~/.lockin/venv
source venv/bin/activate
python -m pip install --upgrade pip 
pip install -r requirements-cli.txt

# Make scirpt executable
chmod +x lockin.sh

style_stdout "Please enter password: "
# Link lockin command to lauch scirpt
sudo ln -fs ~/.lockin/lockin.sh /usr/local/bin/lockin
