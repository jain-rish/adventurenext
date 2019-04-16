#!/bin/bash

sudo apt-get update
sudo apt-get install -y python
sudo apt-get install nginx

wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh
sh Anaconda3-2019.03-Linux-x86_64.sh
source .bashrc

export PATH=~/anaconda3/bin:$PATH
conda create -n natgeo python=3
export PATH=/home/ubuntu/anaconda3/envs/natgeo/bin:$PATH

pip install gunicorn

cd /home
git clone https://github.com/jain-rish/adventurenext.git

