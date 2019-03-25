#!/usr/bin/env php
<?php

$rootDir = rtrim($argv[1] ?? '/Volumes/Kindle', '/');
$dirs = glob("{$rootDir}/documents/*", GLOB_ONLYDIR);
$collectionsPath = "{$rootDir}/system/collections.json";
//$oldCollections = json_decode(file_get_contents($collectionsPath), true);


echo sha1(Normalizer::normalize('/mnt/us/documents/math/Грокаем Алгоритмы. Иллюстрированное пособие для программистов и любопытствущих - Бхаргава А. - 2017.PDF'));
die();

$newCollections = [];
foreach ($dirs as $dir) {
    $colName = basename($dir) . '@en-US';
    $newCollections[$colName]['lastAccess'] = 0;
    $filePaths = array_diff(glob("$dir/*"), glob("$dir/*", GLOB_ONLYDIR));
    foreach ($filePaths as $filePath) {
        $ext = strtolower(pathinfo($filePath, PATHINFO_EXTENSION));
        if (! in_array($ext, ['pdf','mobi'])) {
            echo "No book ext: \"{$filePath}\"\r\n";
            continue;
        }
        $path = '/mnt/us' . substr($filePath, strlen($rootDir));
        $newCollections[$colName]['items'][] = '*' . sha1(Normalizer::normalize($path));
    }
}

$stat = [];

$colNames = array_unique(array_merge(array_keys($newCollections), array_keys($oldCollections)));
foreach ($colNames as $colName) {
    $newCol = $newCollections[$colName] ?? [];
    $newCount = count($newCol['items'] ?? []);
    $oldCol = $oldCollections[$colName] ?? [];
    $oldCount = count($oldCol['items'] ?? []);
    $stat[] = ['name' => substr($colName, 0, -6), 'new' => $newCount, 'old' => $oldCount];
}
usort($stat, function ($a, $b) {
    return abs($a['new']-$a['old']) < abs($b['new']-$b['old']);
});
echo "\r\nStat. New/Old Collection: \r\n";
foreach ($stat as $line) {
    echo "{$line['name']}: {$line['new']}/{$line['old']}" . "\r\n";
}

$ok = rename($collectionsPath, $collectionsPath . '.' . date("Y-m-d-H:i:s"));
if (!$ok) {
    echo "Error while making backup.";
    return;
}
$ok = file_put_contents($collectionsPath, json_encode($newCollections));
if ($ok) {
    echo "\r\nDone!";
}

