#!/bin/bash
sudo apt-get install software-properties-common
sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xcbcb082a1bb943db
sudo add-apt-repository 'deb [arch=amd64,i386] http://ftp.kaist.ac.kr/mariadb/repo/10.1/ubuntu trusty main'
sudo apt-get update
sudo apt-get install mariadb-server
