<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PBL5 Dashboard</title>
  <?php include 'dbconn.php'; ?>
  <style>
    html, body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        margin: 0;
        padding: 0;
        height: 100%;
    }

    .navbar {
        background-color: #333;
        overflow: hidden;
    }

    .navbar a {
        float: left;
        display: block;
        color: #f2f2f2;
        text-align: center;
        padding: 14px 16px;
        text-decoration: none;
    }

    .navbar a:hover {
        background-color: #ddd;
        color: black;
    }

    .main-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 20px;
    }

    .container {
        width: 100%;
        padding: 10px;
        background-color: #fff;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        min-height: 90vh;
    }

    .table-row {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: space-between;
        flex-grow: 1;
    }

    .table-wrapper {
        flex: 1 1 calc(50% - 20px); /* 2 items per row */
        box-sizing: border-box;
        border: 1px solid #ccc;
        padding: 10px;
        background-color: #fafafa;
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .table {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px;
        flex-grow: 1;
    }

    .table-info {
        margin-bottom: 10px;
    }

    .table-info img {
        max-width: 100px; /* Set the max width for the image */
        max-height: 100px; /* Set the max height for the image */
        object-fit: cover; /* Ensure the image retains its aspect ratio */
        margin-bottom: 10px; /* Add space between the image and the text */
    }

    .table-buttons .button {
        padding: 10px 20px;
        background-color: #28a745;
        color: #fff;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .table-buttons .button:hover {
        background-color: #218838;
    }

    iframe {
        width: 70%;
        height: 90vh;
        border: none;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
  </style>
</head>
<body>
<div class="navbar">
  <?php include 'nav_bar.php'; ?>
</div>

<div class="main-content">
  <div class="container">
    <h2>BÀN</h2>
    <?php if ($table_data): ?>
      <div class='table-row'>
        <?php foreach ($table_data as $table_name => $table_details): ?>
          <div class='table-wrapper'>
            <div class='table'>
              <div class='table-info'>
                <img src="table.jpg" alt="Table Image">
                <h3>Bàn: <?= substr($table_name, 3) ?></h3>
              </div>
              <div class='table-buttons'>
                <button id='button-<?= $table_name ?>' class='button' onclick='updateTableStatus("<?= $table_name ?>")'>
                  <?php if($table_details['status'] == 0){
                     echo 'Gọi món'; 
                    } else if($table_details['status'] == 1){
                      echo 'Đang gọi món';
                    } else {
                      echo 'Gọi món thành công';
                    }
                  ?>
                </button>
                <button class='button' onclick='checkTableStatus("<?= $table_name ?>")'>Xem trạng thái</button>
              </div>
            </div>
          </div>
        <?php endforeach; ?>
      </div>
    <?php else: ?>
      <p>No tables found.</p>
    <?php endif; ?>
  </div>

</div>

<script>
// Function to update the status of a table
function updateTableStatus(tableName) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "update_table_status.php", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      alert(xhr.responseText);
      window.location.reload(); // Reload the page after updating the table status
    }
  };
  xhr.send("table_name=" + tableName);
}

function checkTableStatus(tableName) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "check_table_status.php", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status === 200) {
      var status = xhr.responseText;
      alert("Trạng thái gọi món của bàn " + tableName + " là: " + status);
    }
  };
  xhr.send("table_name=" + tableName);
}

// Function to check for new confirmations
function pollForConfirmation() {
  console.log('Polling for confirmation...');
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'poll_for_confirmation.php', true);
  console.log('Sending request...');
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var response = JSON.parse(xhr.responseText);
      console.log('Response:', response);
      if (response.confirmationReceived) {
        alert('Bàn ' + response.table_name + ' đã được xác nhận!');
        updateTableStatus(response.table_name); // Call updateTableStatus when confirmation received
        updateTableButtons(response.table_name); // Update table button text
      }
    }
  };
  xhr.send();
}

function updateTableButtons(tableName) {
  var button = document.getElementById('button-' + tableName);
  if (button) {
    button.textContent = 'Gọi món thành công';
    button.disabled = true; // Optional: disable the button
  }
}

// Start polling when the web page has loaded and repeat every 5 seconds
window.onload = function() {
  setInterval(pollForConfirmation, 5000); // Poll every 5 seconds
};
</script>
</body>
</html>
