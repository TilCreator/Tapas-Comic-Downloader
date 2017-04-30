#Tapastic-Comic-Downloader
This is a downloader to download and update whole comics from Tapastic.com. (Not official!)

##Attention:
**This script could be illegal in certain cases, please first read the terms of service on https://tapas.io/ !**

##Usage:
1. Installing Php (no server only Php):
 * Can be installed on Debian and Ubuntu and other Linux distribution that use 'apt' like this:
 ```
 $ sudo apt install php
 ```
 * On Arch:
 ```
 $ sudo pacman -S php
 ```
2. You have to download the file "downloader.php" (I think the fastest way is copy paste)

3. Set the variables:
 * Open download.php with a text editor
 * Open the first page of the comic, you want to download. If your url looks something like this "https://tapas.io/episode/(number)", you have to write this number in $url, otherwise you can scroll down and back up to hopefully change to url. (Example: 'https://tapas.io/episode/2141' => $url = '2141')
 * Now write the path to the folder, where the images wil be saved, into $path.

4. Run the "downloader.php"!
 * Open a terminal, go to your folder with "downloder.php" (Example ```cd downloads```)
 * Run the "downloader.php"
 ```
 $ php downloader.php
 ```
 * Now this can take a while, this depends on your internet connection and the size of the comic.
 
Sorry for Windows users, but I don't know how you can use Php on Windows (it's possible!). If someone knows this, feel free to write it down here!
