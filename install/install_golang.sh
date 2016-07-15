#!/bin/bash

VERSION=1.6.2
wget https://storage.googleapis.com/golang/go$VERSION.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go$VERSION.linux-amd64.tar.gz

echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.profile
