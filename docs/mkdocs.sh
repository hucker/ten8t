#!/bin/bash
set -e
trap 'echo "Error occured at &LINENO. Command: $BASH_COMMAND"' ERR

python ../src/ten8t/cli/ten8t_cli.py --help > snippets/help.txt
python ../src/ten8t/rich_ten8t/rich_demo.py > snippets/rich_demo.txt
(cd ../src/ten8t/cli && python ten8t_cli.py --json=../../../docs/snippets/result.json  --pkg=../examples/file_system)
radon cc --json   ../src/ten8t/t*.py > snippets/radon_cc.json
radon mi --json   ../src/ten8t/t*.py > snippets/radon_mi.json
radon hal --json  ../src/ten8t/t*.py > snippets/radon_hal.json
python qc_radon.py
python insert_files.py --output=../README.md ../README.md
python add_badges.py
make clean
make html