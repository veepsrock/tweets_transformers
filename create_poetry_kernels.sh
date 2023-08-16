#! /bin/bash
sudo -H pip install poetry
{
    cd ../repos/datascience_etl_and_mle
    dirlist=$(find $l -name '*poetry*' -printf "%h\n" | sort -u)
    for dir in $dirlist
        do (
              cd $dir
              dir_substring=${dir:2}
              poetry install
              poetry run pip install ipykernel
              poetry run python -m ipykernel install --user --name=${dir_substring////_}
              )
        done
} || {
    echo "Repo has not been cloned to this workspace, nothing to do"
}