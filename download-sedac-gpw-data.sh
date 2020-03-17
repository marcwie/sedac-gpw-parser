#!/bin/bash

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
    echo "Keyboard interrupt. Removing temporary files..."
    rm ~/.netrc ~/.urs_cookies
    if [ $STARTED -eq 1 ]
    then 
        rm gpw-v4-population-count-rev11_2020_30_sec_asc.zip
        rm gpw-v4-national-identifier-grid-rev11_30_sec_asc.zip
    fi
    exit
}

STARTED=0

read -p "Enter username for https://urs.earthdata.nasa.gov/home: " USERNAME
read -s -p "Enter password for $USERNAME on https://urs.earthdata.nasa.gov/home: " PASSWORD

touch ~/.netrc
echo "machine urs.earthdata.nasa.gov login $USERNAME password $PASSWORD" > ~/.netrc
chmod 0600 ~/.netrc

STARTED=1

wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies --auth-no-challenge -O gpw-v4-population-count-rev11_2020_30_sec_asc.zip https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/gpw-v4-population-count-rev11/gpw-v4-population-count-rev11_2020_30_sec_asc.zip
wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies --auth-no-challenge -O gpw-v4-national-identifier-grid-rev11_30_sec_asc.zip https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/gpw-v4-national-identifier-grid-rev11/gpw-v4-national-identifier-grid-rev11_30_sec_asc.zip

echo "Removing temporary files..."
rm ~/.netrc ~/.urs_cookies
