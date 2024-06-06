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
    $audioIdA = (int) $a['audioId'];
    $audioIdB = (int) $b['audioId'];

    if ($audioIdA < $audioIdB) {
        return 1; // $a should come after $b (descending order)
    } elseif ($audioIdA > $audioIdB) {
        return -1; // $a should come before $b (descending order)
    } else {
        return 0; // $a and $b are equal
    }
});

// Get the first 5 items (5 newest files based on audioId)
$latestAudioData = array_slice($audioData, 0, 5);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Audio Results</title>
    <link rel="stylesheet" href="audio_details.css">
</head>
<body>
    <div class="navbar">
        <?php include 'nav_bar.php'; ?>
    </div>
    <div class="container">
        <h2>Các kết quả dự đoán</h2>
        <div id="audioList"></div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const audioListContainer = document.getElementById('audioList');

            // Function to render audio items
            const renderAudioItems = (data) => {
                // Clear previous content
                audioListContainer.innerHTML = '';

                // Render each audio item
                data.forEach(audioItem => {
                    const audioId = audioItem.audioId;
                    const result = audioItem.result;

                    // Create audio item element
                    const div = document.createElement('div');
                    div.classList.add('audio-item');

                    // Populate audio item content
                    const heading = document.createElement('h3');
                    heading.textContent = `Audio ID: ${audioId}`;
                    const resultParagraph = document.createElement('p');
                    resultParagraph.textContent = `Result: ${result}`;

                    // Append content to audio item
                    div.appendChild(heading);
                    div.appendChild(resultParagraph);

                    // Append audio item to container
                    audioListContainer.appendChild(div);
                });
            };

            // Render audio items initially
            renderAudioItems(<?php echo json_encode($latestAudioData); ?>);

            // Function to update audio items periodically
            const updateAudioItems = () => {
                // Fetch updated audio data using AJAX (or other methods)
                fetch('fetch_latest_audio.php') // Assuming you have a PHP endpoint to fetch latest audio data
                    .then(response => response.json())
                    .then(data => {
                        renderAudioItems(data); // Render the updated audio items
                    })
                    .catch(error => {
                        console.error('Error fetching latest audio data:', error);
                    });
            };

            // Periodically update audio items every 10 seconds (adjust as needed)
            setInterval(updateAudioItems, 10000); // Update every 10 seconds (10000 milliseconds)
        });
    </script>
</body>
</html>
