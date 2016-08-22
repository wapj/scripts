#!/bin/bash

## install Composer
### download installer file 

curl -O -L https://getcomposer.org/installer
php installer

### check version
php composer.phar --version

### move to path
sudo mv composer.phar /usr/local/bin/composer

