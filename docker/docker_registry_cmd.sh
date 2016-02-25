#!/bin/bash
PARAM=${1:-"list"}

### docker-registry에 올린 컨테이너 명
CONTAINER=${2:-"server"}

### docker-registry에 접근가능한 도메인을 설정해야함.
DOMAIN="https://deploy.gyus.com:5443" 

function usage() {
    echo "[USAGE] $0 [list|catalog] [$CONTAINER]"
}


### tag_list의 경우는 container명이 필요함.
if [ "$PARAM" = "list" ];then
    curl -X GET $DOMAIN/v2/$CONTAINER/tags/list
fi

if [ "$PARAM" = "catalog" ];then
    curl -X GET $DOMAIN/v2/_catalog
fi
