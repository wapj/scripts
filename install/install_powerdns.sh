#!/bin/bash
sudo apt-get update && apt-get upgrade -y
sudo apt-get install software-properties-common
sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xcbcb082a1bb943db
sudo add-apt-repository 'deb http://ftp.kaist.ac.kr/mariadb/repo/5.5/ubuntu trusty main'
sudo apt-get -y install libaio1 libdbd-mysql-perl libdbi-perl libmariadbclient18 libmysqlclient18 libnet-daemon-perl libplrpc-perl mariadb-client-5.5 mariadb-client-core-5.5 mariadb-common mysql-common mariadb-server mariadb-server-5.5 mariadb-server-core-5.5

if [ -f powerdns_init.sql ];then
    mysql -u root -p < ~/powerdns_init.sql
else
    echo "[WARNING] initialize powerdsn db manualy!"
fi

echo "deb [arch=amd64] http://repo.powerdns.com/ubuntu trusty-auth-40 main" >> sudo /etc/apt/sources.list

sudo touch "/etc/apt/preferences.d/pdns"
echo -e  "Package: pdns-*\nPin: origin repo.powerdns.com\nPin-Priority: 600" >> "/etc/apt/preferences.d/pdns"

curl https://repo.powerdns.com/FD380FBB-pub.asc | sudo apt-key add - &&
sudo apt-get install -y pdns-server pdns-backend-mysql
sudo apt-get -f purge -y mysql-client
rm /etc/powerdns/pdns.d/*
