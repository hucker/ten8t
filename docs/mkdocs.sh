#!/bin/bash

radon cc --json   ../src/ten8t/t*.py > radon_cc.json
radon mi --json   ../src/ten8t/t*.py> radon_mi.json
radon hal --json  ../src/ten8t/t*.py> radon_hal.json
python qc_rad.py
python insert_files.py
python add_badges.py
make clean
make html