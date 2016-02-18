#!/bin/bash

which `yum`
IS_CENTOS=$?

install_centos() {
    sudo yum update
    sudo tee /etc/yum.repos.d/docker.repo <<-'EOF'
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

if [ IS_CENTOS = 0 ];then
    install_centos
    echo "FINISH INSTALL DOCKER"
else
    install_ubuntu
    echo "FINISH INSTALL DOCKER"
fi
