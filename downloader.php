<?php

$url = '';           // Number on the end of the url, if you open the first page of the comic.   (Example: 'https://tapastic.com/episode/2141' => '2141')
$comic = '';         // Name of the comic (Only for naming the images)                           (Example: 'RavenWolf')
$path = $comic.'/';  // Path to save (Has to end with a '/')                                     (Example: $comic.'/' (To save the comic in a subfolder with the name of the comic))

$count = 1;
if (file_exists($path.'updaterLast.php')) {
    include $path.'updaterLast.php';
    echo 'Found "'.$path.'updaterLast.php'.'" (If you want to download the comic new, delete this file. Now it will only update.)'."\n";
} else {
    if ($url == '') {
        exit('$url is not set!'."\n");
    }
}
if (!file_exists($path)) {
    mkdir($path);
    echo 'There was no Folder "'.$path.'"! Now there is! (Or at least should be...)'."\n";
}
echo "\n\n".'https://tapastic.com/episode/'.$url;
while (true) {
    if ($count < 10) {
        $fill = '000';
    } elseif ($count < 100) {
        $fill = '00';
    } elseif ($count < 1000) {
        $fill = '0';
    } else {
        $fill = '';
    }
    $site = preg_replace("/\s+/", '', preg_replace("/[\r\n]+/", '', file_get_contents('https://m.tapastic.com/episode/'.$url.'?site_preference=mobile')));
    $imgUrl = get_string_between($site, '<articleclass="art-image-wrap">', '</article>');
    if ($imgUrl == '') {
        file_put_contents($path.'updaterLast.php', '<?php'."\n".'$url = '."'".$url."'".';'."\n".'$count = '."'".($count-1)."'".';');
        echo '  =>  '.'updaterLast.php'."\n\n\n".'Finished!'."\n";
        break;
    }
    if (strlen($imgUrl) < 250) {
        $imgUrl = get_string_between(get_string_after($imgUrl, '<imgclass="art-image"src=', 100), '"', '"');
        echo "\n".$imgUrl;
        $img = file_get_contents($imgUrl);
        if (stripos($imgUrl, '.png')) {
            $type = '.png';
        } elseif (stripos($imgUrl, '.jpg')) {
            $type = '.jpg';
        } elseif (stripos($imgUrl, '.gif')) {
            $type = '.gif';
        }
        file_put_contents($path.$comic.$fill.$count.$type, $img);
        echo '  =>  '.$comic.$fill.$count.$type."\n\n";
        ++$count;
    } else {
        for ($i = substr_count($imgUrl, '<imgclass="art-image"src="'); $i > 0; --$i) {
            $imgUrlPart = get_string_between(get_string_after($imgUrl, '<imgclass="art-image"src=', 100), '"', '"');
            $imgUrl = substr($imgUrl, stripos($imgUrl, '">')+2, strlen($imgUrl) - stripos($imgUrl, '">'));
            echo $imgUrlPart;
            $img = file_get_contents($imgUrlPart);
            if (stripos($imgUrlPart, '.png')) {
                $type = '.png';
            } elseif (stripos($imgUrlPart, '.jpg')) {
                $type = '.jpg';
            } elseif (stripos($imgUrlPart, '.gif')) {
                $type = '.gif';
            }
            file_put_contents($path.$comic.$fill.$count.$type, $img);
            echo '  =>  '.$comic.$fill.$count.$type."\n";
            ++$count;
        }
        echo "\n";
    }
    if (get_string_between($site, '</span><ahref="/episode/', '"class="cellnext') == '') {
        file_put_contents($path.'updaterLast.php', '<?php'."\n".'$url = '."'".$url."'".';'."\n".'$count = '."'".($count-1)."'".';');
        echo '  =>  '.'updaterLast.php'."\n\n\n".'Finished!'."\n";
        break;
    } else {
        $url = get_string_between($site, '</span><ahref="/episode/', '"class="cellnext');
    }
    echo 'https://tapastic.com/episode/'.$url;
}

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

function get_string_after($string, $start, $len) {
    $string = ' '.$string;
    $ini = strpos($string, $start);
    if ($ini == 0) {
        return '';
    }
    $ini += strlen($start);

    return substr($string, $ini, $len);
}
