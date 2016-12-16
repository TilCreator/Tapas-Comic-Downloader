#Tapastic-Comic-Downloader
This is a downloader to download and update whole comics from Tapastic.com! (Not official)

##Attention:
**The use of this script could be illegal in your country!
To my knowledge it should be legal to use it in Germany (I can not guarantee it).**

##Usage:
1. Installing Php (no server only Php):
 * Can be installed on Debian and Ubuntu and other Linux distribution that use 'apt' like this:
 ```
 $ sudo apt install php
 ```

2. You have to download the file "downloader.php" (I think the fastest way is copy paste)

3. Set the variables:
 * Open download.php with a text editor
 * Open the first page of the comic, you want to download. If your url looks something like this "https://tapastic.com/episode/(number)", you have to write this number in $url, otherwise scroll down and back up, your url should now be changed. (Example: 'https://tapastic.com/episode/2141' => $url = '2141')
 * Set $comic to the name of your comic (This only for naming the images, you could set it to anything! But don't leave it empty!)
 * *(optional)* You can set the path to the folder, where the images wil be saved. If you keep it as it is, it will generate a subfolder with the name of $comic.

4. Run the "downloader.php"!
 * Open a terminal, go to your folder with "downloder.php" (Example ```cd downloads```)
 * Run the "downloader.php"
 ```
 $ php downloader.php
 ```
 * Now this can take a while, this depends on your internet connection and the size of the comic.
 
5. Update downloaded content:
 * If you now run the script again, it will only update from the last page downloaded. This is saved in the file "updaterLast.php" in $path. If you like to download the comic again, you have to delet this file.

Sorry for Windows users, but I don't know how you can use Php on Windows (it's possible!). If someone knows this, feel free to write it down here!
