#!/bin/bash

# Set up virtual environment
setup_venv() {
    if [ -d "venv" ]; then
        sudo rm -rf venv
    fi
    # sudo python -m venv --system-site-packages venv
    # source venv/bin/activate
    sudo apt-get update
}

# Install packages
install_packages() {
    local package_file=$1
    local package_manager=$2
    local install_command=$3

    local failed_file="failed_${package_manager}_packages.txt"
    echo __Installing...

    while IFS= read -r package; do
        if [[ "${package:0:1}" != "#" ]]; then
            echo __ $install_command $package
            sudo $install_command $package || echo "Failed to install $package" >> $failed_file
        fi
    done < $package_file
}

# Main script
setup_venv

# system level packages
xargs sudo apt-get -y install < requiredPackage.txt

# python app dependencies
install_packages "requirements.txt" "pip" "pip install"
