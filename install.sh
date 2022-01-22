#! /bin/bash

# If virtualenv not installed, download & install it for user
if ! python3 -c "import virtualenv" &> /dev/null; then
    python3 -m pip install --user virtualenv
fi

# Create  virtual env for python dependencies
virtualenv venv
source venv/bin/activate

# Install briefcase
pip install briefcase

# Build app template
briefcase build

# Package app template to build disk image
briefcase package --no-sign

# Open disk image to promp user and install
open macOS/LockIn-0.0.1.dmg
