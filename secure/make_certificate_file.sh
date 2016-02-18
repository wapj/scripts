#!/bin/bash

### 인증서 만드는 명령어 정리

### key -> csr -> crt

### 키생성
openssl genrsa -out deploy-server.key 2048

### 인증서 서명 요청 파일 생성 (Certificate siging request)
### 요거 실행하면 이것저것 물어봄
openssl req -new -key deploy-server.key -out deploy-server.csr


### 인증서 생성
openssl x509 -req -days 365 -in deploy-server.csr -signkey deploy-server.key -out deploy-server.crt


### 시스템에 설치 (ubuntu)

sudo cp deploy-server.crt /usr/share/ca-certificates/
echo "deploy-server.crt" | sudo tee -a /etc/ca-certificates.conf
sudo update-ca-certificates


### 시스템에 설치(centos)
sudo cp deploy-server.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust enable
sudo update-ca-trust extract
