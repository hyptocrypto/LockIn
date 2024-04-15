#`  ! /bin/bash 

function style_stdout () {
    echo -e "\033[0;32m $1 \033[0m"
}
function error_style_stdout () {
    echo -e "\033[0;31m $1 \033[0m"
}

#User input
read -p "Please enter your name: " HOST_NAME
read -p "Please enter sudo password: " PASSWORD
echo -e "\n" 

read -r -p "Please enter network share host location. Example: //guest:@192.168.1.69/NAS. Press enter to skip " NAS_HOST
echo -e "\n"
read -r -p "Please enter local network share mount point. Example: /Volumes/NAS/. Press enter to skip. " NETWORK_SHARE

if [ -z $NETWORK_SHARE ]
    then
    NETWORK_SHARE="/Volumes/NAS"
    echo 'Using defualt network volume /Volumes/NAS'
fi
if [ -z $NAS_HOST ]
    then
    NAS_HOST="//guest:@192.168.1.69/NAS"
    echo 'Using defualt network volume host //guest:@192.168.1.69/NAS'
fi

if [ -z $HOST_NAME ] || [ -z $PASSWORD ]
then
   error_style_stdout "Name and password are required."
   exit 1
fi

# Target strings to up date in settings file
HOST_TARGET_KEY="HOST"
PASSWORD_KEY="PASSWORD"
NET_SHARE_TARGET_KEY="NETWORK_SHARE_URI"
NAS_HOST_KEY="NAS_HOST"

# Ensure python3.10 is install and linked
style_stdout "Cheking for python 3.10"
brew install python@3.10
brew link --force python@3.10

mkdir ~/.lockin
cp lockin.sh requirements-cli.txt src/lockin/__init__.py src/lockin/cli.py src/lockin/manager.py src/lockin/cli_styles.py src/lockin/exceptions.py src/lockin/settings.py src/lockin/models.py src/lockin/smb.py src/lockin/loader.py ~/.lockin

cd ~/.lockin

# Location of lockin settings file
SETTINGS_FILE="./settings.py"

# Replace strings in settings file
sed -i -e "s|\($HOST_TARGET_KEY *= *\).*|\1'$HOST_NAME'|" $SETTINGS_FILE
sed -i -e "s|\($PASSWORD_KEY *= *\).*|\1'$PASSWORD'|" $SETTINGS_FILE
sed -i -e "s|\($NET_SHARE_TARGET_KEY *= *\).*|\1'$NETWORK_SHARE'|" $SETTINGS_FILE
sed -i -e "s|\($NAS_HOST_KEY *= *\).*|\1'$NAS_HOST'|" $SETTINGS_FILE

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

# Link lockin command to lauch scirpt
if [ ! -d "/usr/local/bin" ]; then
    echo $PASSWORD|sudo -S mkdir /usr/local/bin
fi
echo $PASSWORD|sudo -S ln -fs ~/.lockin/lockin.sh /usr/local/bin/lockin
