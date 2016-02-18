#!/bin/bash


PLATFORM="centos"

if [ -f /etc/lsb-release ]; then
    PLATFORM="ubuntu"
fi

# EOF 사용시에 EOF들어가는거는 스페이스 넣으면 안됨
install_centos() {
sudo yum update
sudo tee /etc/yum.repos.d/docker.repo <<-EOF
[dockerrepo]
name=Docker Repository
baseurl=https://yum.dockerproject.org/repo/main/centos/$releasever/
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg
EOF
sudo yum install docker-engine
sudo service docker start
sudo docker run hello-world
}

install_ubuntu() {
    sudo apt-get update
    sudo apt-get install docker-engine
    sudo service docker start
    sudo docker run hello-world
   
}

if [ "$PLATFORM" = "centos" ];then
    install_centos
    echo "FINISH INSTALL DOCKER"
else
    install_ubuntu
    echo "FINISH INSTALL DOCKER"
fi
