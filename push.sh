#!/bin/bash
###
### 변경된 걸 그냥 푸시하고 싶을때 사용 
###

usage() {
    echo "usage : $0 -m message"
    exit 1
}


while getopts ":m:" opt; do
    case $opt in
        m) MSG="$OPTARG";;
        \?) usage_exit;;
    esac
done

shift $((OPTIND - 1))

if [ -n "$MSG" ]; then
    cd `pwd`
    git pull origin master
    git add .
    git commit -m "$MSG"
    git push origin master
else
    echo "[WARN] Please input commit message."
    usage
    exit 1
fi


