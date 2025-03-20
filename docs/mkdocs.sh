#!/bin/bash

python ../src/ten8t/cli/ten8t_cli.py --help > snippets/help.txt
python ../src/ten8t/rich_ten8t/rich_demo.py > snippets/rich_demo.txt
#python ../src/ten8t/cli/ten8t_cli.py  --pkg=../src/examples/file_system  > snippets/result.json
radon cc --json   ../src/ten8t/t*.py > snippets/radon_cc.json
radon mi --json   ../src/ten8t/t*.py > snippets/radon_mi.json
radon hal --json  ../src/ten8t/t*.py > snippets/radon_hal.json
python qc_rad.py
#python insert_files.py ../README.md > ../README.MD
python add_badges.py
make clean
make html