<?php
// Include Firebase PHP SDK setup
include 'dbconn.php';

// Fetch audio data from Firebase
$ref_audio = 'audio_results';
$fetch_data = $database->getReference($ref_audio)->getValue();

// Convert Firebase data to PHP array
$audioData = [];
foreach ($fetch_data as $key => $value) {
    $audioData[] = $value;
}

// Sort audio data based on audioId in descending order
usort($audioData, function ($a, $b) {
    return $b['audioId'] - $a['audioId'];
});

// Get the first 5 items (5 newest files based on audioId)
$latestAudioData = array_slice($audioData, 0, 5);

// Return latest audio data as JSON response
header('Content-Type: application/json');
echo json_encode($latestAudioData);
?>
