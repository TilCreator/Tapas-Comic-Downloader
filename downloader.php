<?php

$episode = ''; // Number on the end of the url, if you open the first page of the comic. (Example: 'https://tapas.io/episode/2141' => '2141')
$path = '';    // Path to save (Has to end with a '/') (Example: 'Ravenwolf/')

// Define needed functions
function get_string_between($string, $start, $end) {
    $string = ' '.$string;
    $ini = strpos($string, $start);
    if ($ini == 0) {
        return '';
    }
    $ini += strlen($start);
    $len = strpos($string, $end, $ini) - $ini;

    return substr($string, $ini, $len);
}

$imgUrls = null;
$rawImgUrls = null;

$pageNumber = 0;
$lastImg = 0;

// Test input for erros
if (empty($episode)) {
    die('Error: $episode mustn\'t be empty.');
}

if (empty($path)) {
    die('Error: $path mustn\'t be empty.');
}

if (substr($path, -1) != '/') {
    die('Error: $path has to end with /.');
}

if (!file_exists($path)) {
    mkdir($path);
    echo($path." created.\n\n");
}

while (!empty($episode)) {

    // Get html site with last comic page
    $site = preg_replace("/\s+/", '', preg_replace("/[\r\n]+/", '', file_get_contents('https://m.tapas.io/episode/'.$episode.'?site_preference=mobile')));

    // Write pages to array
    $rawImgUrls = explode('<imgclass="art-image"src="', get_string_between($site, '<articleclass="art-image-wrap">', '</article>'));
    $i = 0;
    foreach ($rawImgUrls as $rawImgUrl) {
        if (!empty($rawImgUrl)) {
            $imgUrls[$i] = substr($rawImgUrl, 0, stripos($rawImgUrl, '"width'));
            $i++;
        }
    }

    // Download page(s)
    if (count($imgUrls) > 0) {

        $type = substr($imgUrls[$lastImg], -4);
        $file = file_get_contents($imgUrls[$lastImg]);
        file_put_contents($path.sprintf('%04d', $pageNumber).$type, $file);

        echo($path.sprintf('%04d', $pageNumber).$type.' ('.$imgUrls[$lastImg].') saved!'."\n");

        if (count($imgUrls)-1 == $lastImg || count($imgUrls)-1 == 0) {
            $episode = get_string_between($site, '</span><ahref="/episode/', '"class="cellnext');
        } else {
            $lastImg++;
        }

        $pageNumber++;

    } else {
        break;
    }

}

echo("\n\nFinished!");
