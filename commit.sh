#!/bin/bash -e
# chmod +x commit.sh
# ./commit.sh 'my'commit'message'
commit_message="$1"
git add . -A
git commit -m "$commit_message"
git push -u origin master