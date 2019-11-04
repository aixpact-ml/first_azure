#!/bin/bash -e
# chmod +x commit.sh
# ./commit.sh 'my'commit'message'
commit_message="$1"
git add . -A
git commit -m "$commit_message"
git push -u origin master


# delete remote file and keep local file
# git rm --cached somefile.ext
# git rm --cached Dockerfile *.yml
# then commit