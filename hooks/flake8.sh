set -e

pwd=$(pwd)
files=$(python $pwd/hooks/find_py_files.py)
if [ ! -z "$files" ]
then
    flake8 ${files}
fi
