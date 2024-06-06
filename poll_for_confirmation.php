<?php
require __DIR__ . '/vendor/autoload.php';

use Kreait\Firebase\Factory;

// Initialize the factory with the service account and database URI
$factory = (new Factory)
    ->withServiceAccount('pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json')
    ->withDatabaseUri('https://pbl5-nhom7-default-rtdb.asia-southeast1.firebasedatabase.app/');

// Create an instance of the Firebase Realtime Database directly from the factory
$database = $factory->createDatabase();

// Function to fetch the latest audio data from Firebase
function fetchLatestAudioData($database) {
    $ref_audio = 'audio_results';
    $fetch_data = $database->getReference($ref_audio)->getValue();

    $audioData = [];
    foreach ($fetch_data as $key => $value) {
        $audioData[$key] = $value;
    }

    uasort($audioData, function ($a, $b) {
        $audioIdA = (int) $a['audioId'];
        $audioIdB = (int) $b['audioId'];

        return $audioIdB <=> $audioIdA;
    });

    return array_slice($audioData, 0, 2, true); // Return the keys of the two latest audio data
}

// Function to get a table with status 1
function getTableWithStatusOne($database) {
    $tableWithStatusOne = '';

    $tablesRef = $database->getReference('tables')->getValue();
    foreach ($tablesRef as $tableName => $tableDetails) {
        if ($tableDetails['status'] == 1) {
            $tableWithStatusOne = $tableName;
            break;
        }
    }

    return $tableWithStatusOne;
}

// Check the table status and return the result
$latestAudioData = fetchLatestAudioData($database);

if (count($latestAudioData) < 2) {
    echo json_encode(['confirmationReceived' => false, 'table_name' => '']);
    exit;
}

$latestAudioKeys = array_keys($latestAudioData);
$latestAudioValues = array_values($latestAudioData);

$confirmationReceived = false;

$table_name = getTableWithStatusOne($database);

if ($table_name && isset($latestAudioValues[0]['result']) && isset($latestAudioValues[1]['result'])) {
    $latestAudioResult1 = $latestAudioValues[0]['result'];
    $latestAudioResult2 = $latestAudioValues[1]['result'];

    if ($latestAudioResult1 === 'Xác nhận' && $latestAudioResult2 === 'Xác nhận') {
        $currentStatus = $database->getReference('tables/' . $table_name . '/status')->getValue();
        if ($currentStatus == 1) {
            // Wait for 5 seconds before taking action
            sleep(5);

            // Set confirmation received to true
            $confirmationReceived = true;

            // Delete the 'Xác nhận' audio results from Firebase
            $database->getReference('audio_results/' . $latestAudioKeys[0])->remove();
            $database->getReference('audio_results/' . $latestAudioKeys[1])->remove();
        }
    }
}

echo json_encode(['confirmationReceived' => $confirmationReceived, 'table_name' => $table_name]);
?>
