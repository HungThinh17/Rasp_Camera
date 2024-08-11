#!/bin/bash

sudo apt-get update
sudo apt-get upgrade

# This requires user to confirm several steps.
sudo apt-get install mariadb-server -y
sudo mysql_secure_installation

# Create a new database and user

## sudo mysql -u root -p
#$ CREATE DATABASE slidb;
#$ CREATE USER 'dgmsli'@'localhost' IDENTIFIED BY 'digime';
## GRANT ALL PRIVILEGES ON dgmsli.* TO 'dgmsli'@'localhost';
## FLUSH PRIVILEGES;

# Verify the installation
# sudo mysql -u dgmsli -p
