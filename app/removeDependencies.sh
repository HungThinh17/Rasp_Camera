#!/bin/bash

# Set up virtual environment
setup_venv() {
    if [ -d "venv" ]; then
        rm -rf venv
    fi
    python3 -m venv venv
    source venv/bin/activate
    sudo apt-get update
}

# Install packages
install_packages() {
    local package_file="$1"
    local package_manager="$2"
    local install_command="$3"
    local failed_file="failed_${package_manager}_packages.txt"

    while IFS= read -r package; do
        if [[ "${package:0:1}" != "#" ]]; then
            echo "Installing $package with $package_manager"
            $install_command "$package" || {
                echo "Failed to install $package" >> "$failed_file"
                exit_code=$?
            }
        fi
    done < "$package_file"

    if [ -f "$failed_file" ]; then
        echo "Some packages failed to install. Check $failed_file for details."
    fi

    return $exit_code
}

# Main script
setup_venv

# system level packages
xargs sudo apt-get -y remove < requiredPackage.txt

# python app dependencies
install_packages "requirements.txt" "pip" "pip install" || exit 1
