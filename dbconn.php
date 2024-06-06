<?php

require __DIR__ . '/vendor/autoload.php';

use Kreait\Firebase\Factory;

$factory = (new Factory)
    ->withServiceAccount('pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json')
    ->withDatabaseUri('https://pbl5-nhom7-default-rtdb.asia-southeast1.firebasedatabase.app/');

$database = $factory->createDatabase();

$tables_ref = $database->getReference('tables');
$tables_snapshot = $tables_ref->getSnapshot();
$table_data = $tables_snapshot->getValue();

?>