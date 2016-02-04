#!/bin/bash
usage () {
    echo "usage : $0 user@repository_domain"    
}

cd `pwd`

if [ -z $1 ];then
    usage
    exit -1
fi

git init
git add --all
git commit -m "initial commit"
git remote add origin $1
git push origin master
