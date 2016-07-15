#!/bin/bash

if [ -f /etc/lsb-release ]; then
    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils git
elif [ -f /etc/redhat-release ]; then
    sudo yum install -y zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel git gcc
fi

curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"'  >> ~/.bashrc

source ~/.bashrc

sleep 1

pyenv install 3.5.2
pyenv virtualenv 3.5.2 py35
pyenv activate py35
