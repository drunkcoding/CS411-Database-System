#!/bin/sh

apt-get update
apt-get install mariadb-client mariadb-server libmariadb-dev zlibc zlib1g-dev libssl-dev
pip3 install -r ./requirements.txt
