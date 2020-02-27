# Tapastic-Comic-Downloader
This is a downloader to download and update whole comics from https://tapas.io/. (Not official!)

## Attention:
**This script could be illegal in certain cases, please first read the terms of service on https://tapas.io/ !**

## Usage:
1. Installing Python3 and needed modules:
 * Can be installed on Debian and Ubuntu and other Linux distribution that use 'apt' like this:
 ```
 # apt install python3 python3-dev python3-pip libxml2-dev libxslt1-dev zlib1g-dev
 # pip3 install -r requirenments.txt
 # pip3 install -r requirenments_novels.txt  # If novels are expected to be downloaded
 ```
 * On Arch/Antergos:
 ```
 # pacman -S python python-pip
 # pip install -r requirenments.txt
 # pip install -r requirenments_novels.txt  # If novels are expected to be downloaded
 ```
 + If someone got it running on another OS, please let me know!
2. Get input link
 * Go to the comic you want to download (any page)
 * Rightclick on the comic name in the upper left corner and select "Copy linkaddress" (Or similar) or just use the name behind series in the url.
 * Examples: `https://tapas.io/series/Erma`, `RavenWolf`, ...
3. Start the download
 * Usage of `tapas-dl.py`:
 ```
 $ tapas-dl.py [-h/--help] [-f/--force] [-v/--verbose] URL/name [URL/name ...]
 ```
 * The script will create an folder with the name and urlName (`name [urlName]`) of the comic in the current shell location (like git) and download all images of the comic into it.
 * If the script finds an folder with the name of the comic, it will only update, this can be disabled with `-f/--force`.
 * To get the verbose output use `-v/--verbose`.

### Extra:
If someone wants to quickly understand the code, here is the pseudo code of the pure download part:
1. Get comic start page (Example: `https://tapas.io/series/Erma`)
2. Extract all pageIds of the comic from the `_data` JS object from the start page
3. Get image urls by extracting them out of `https://tapas.io/episode/view/<pageId>` (Example: `https://tapas.io/episode/view/255222`)
4. Download the images
