#!/bin/bash

BASE_URL=https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/

PROJECT_FOLDER=$HOME/.sedac_gpw_parser/

POPULATION_FILE=gpw-v4-population-count-rev11_2020_30_sec_asc.zip 
POPULATION_MD5_REF=7a5dd42681fa679d147e6bd126d322db
POPULATION_FOLDER=gpw-v4-population-count-rev11_2020_30_sec_asc
POPULATION_URL=${BASE_URL}gpw-v4-population-count-rev11/gpw-v4-population-count-rev11_2020_30_sec_asc.zip

GRID_FILE=gpw-v4-national-identifier-grid-rev11_30_sec_asc.zip
GRID_MD5_REF=41c68dc4b5c9dccacba3fe38c9b5a3cf
GRID_FOLDER=gpw-v4-national-identifier-grid-rev11_30_sec_asc
GRID_URL=${BASE_URL}gpw-v4-national-identifier-grid-rev11/gpw-v4-national-identifier-grid-rev11_30_sec_asc.zip

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function clean() {
    echo "Removing temporary files..."

    if [ -e ~/.netrc ]
    then
        echo "Removing temporary .netrc from HOME"
        rm ~/.netrc 
    fi

    if [ -e ~/.urs_cookies ]
    then
        echo "Removing temporary cookies from HOME"
        rm ~/.urs_cookies
    fi
}

function ctrl_c() {
    echo "Keyboard interrupt."
    clean
    if [ -d $PROJECT_FOLDER$GRID_FOLDER ]
    then
        rm -r $PROJECT_FOLDER$GRID_FOLDER
    fi
    
    if [ -d $PROJECT_FOLDER$POPULATION_FOLDER ]
    then
        rm -r $PROJECT_FOLDER$POPULATION_FOLDER
    fi
    exit
}

function get_data() {
    read -p "Enter username for https://urs.earthdata.nasa.gov/home: " USERNAME
    read -s -p "Enter password for $USERNAME on https://urs.earthdata.nasa.gov/home: " PASSWORD
    
    touch ~/.netrc
    echo "machine urs.earthdata.nasa.gov login $USERNAME password $PASSWORD" > ~/.netrc
    chmod 0600 ~/.netrc
    
    if [ $DOWNLOAD_GRID == 1 ]
    then
        wget --continue --load-cookies ~/.urs_cookies \
            --save-cookies ~/.urs_cookies --keep-session-cookies \
            --auth-no-challenge -O $PROJECT_FOLDER$GRID_FILE $GRID_URL
    fi
    
    if [ $DOWNLOAD_POP == 1 ]
    then
        wget --continue --load-cookies ~/.urs_cookies \
            --save-cookies ~/.urs_cookies --keep-session-cookies \
            --auth-no-challenge -O $PROJECT_FOLDER$POPULATION_FILE $POPULATION_URL
    fi

    clean
}


if [ ! -d $PROJECT_FOLDER ]
then
    mkdir $PROJECT_FOLDER
fi

DOWNLOAD_POP=1
if [ -e $PROJECT_FOLDER$POPULATION_FILE ]
then
    POPULATION_MD5=$(md5sum $PROJECT_FOLDER$POPULATION_FILE)
    POPULATION_MD5=${POPULATION_MD5:0:32}
    if [ $POPULATION_MD5 = $POPULATION_MD5_REF ]
    then
        DOWNLOAD_POP=0
        echo "Population data is present and md5sum is valid."
    fi
fi

DOWNLOAD_GRID=1
if [ -e $PROJECT_FOLDER$GRID_FILE ]
then
    GRID_MD5=$(md5sum $PROJECT_FOLDER$GRID_FILE)
    GRID_MD5=${GRID_MD5:0:32}
    if [ $GRID_MD5 = $GRID_MD5_REF ]
    then
        DOWNLOAD_GRID=0
        echo "Grid is present and md5sum is valid."
    fi
fi

if
    [ $DOWNLOAD_POP == 1 ] || [ $DOWNLOAD_GRID == 1 ]
then
    echo "At least one file is missing or invalid. Downloading..."
    get_data
fi

if [ ! -d $PROJECT_FOLDER$GRID_FOLDER ]
then
    unzip $PROJECT_FOLDER$GRID_FILE -d $PROJECT_FOLDER$GRID_FOLDER
fi

if [ ! -d $PROJECT_FOLDER$POPULATION_FOLDER ]
then
    unzip $PROJECT_FOLDER$POPULATION_FILE -d $PROJECT_FOLDER$POPULATION_FOLDER
fi

clean
