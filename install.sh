#! /bin/bash

virtualenv venv
source venv/bin/activate

pip install briefcase

briefcase build
briefcase package --no-sign

open macOS/LockIn-0.0.1.dmg
