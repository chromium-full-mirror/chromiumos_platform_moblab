set -e

pwd=$(pwd)
files=$(python $pwd/hooks/find_py_files.py)

if [ ! -z "$files" ]
then
    black --line-length=79 ${files}
fi
