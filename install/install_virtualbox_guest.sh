#!/bin/bash
sudo sed -i 's/kr.archive.ubuntu.com/ftp.daum.net/g' /etc/apt/sources.list
sudo sed -i 's/archive.ubuntu.com/ftp.daum.net/g' /etc/apt/sources.list
sudo apt-get update 
sudo apt-get dist-upgrade -y
sudo apt-get install virtualbox-guest-x11 -y
