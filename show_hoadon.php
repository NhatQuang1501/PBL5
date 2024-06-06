<?php
// Include Firebase PHP SDK setup
include 'dbconn.php';

// Fetch food order details from Firebase
$ref_audio = 'food_details';
$fetch_data = $database->getReference($ref_audio)->getValue();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PBL5 Dashboard</title>
    <link rel="stylesheet" href="hoadon.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
<div class="navbar">
    <?php include 'nav_bar.php'; ?>
</div>
<div class="container">
    <h2>DANH SÁCH HÓA ĐƠN</h2>
    <div class="table-responsive">
        <table class="table table-bordered">
            <thead>
            <tr>
                <th>STT</th>
                <th>Mã hóa đơn</th>
                <th>Bàn</th>
                <th>Thời gian</th>
                <th></th>
            </tr>
            </thead>
            <tbody>
            <?php
            // Initialize a counter for invoice numbers
            $invoice_counter = 1;

            // Loop through each entry in $fetch_data (assuming it's an associative array of orders)
            foreach ($fetch_data as $key => $order) {
                // Extract details from the key
                $split_key = explode('-', $key);
                $table = $split_key[0]; // Extract table name (e.g., 'Ban1')
                $table_number = preg_replace('/\D/', '', $table);
                $invoice_id = $split_key[1]; // Extract invoice ID (e.g., '102')
                $time = $split_key[2]; // Extract time (e.g., '8:50:20 24:12:2023')

                // Display a row in the table for each order
                echo "<tr>";
                echo "<td>$invoice_counter</td>";
                echo "<td>$invoice_id</td>";
                echo "<td>$table_number</td>";
                echo "<td>$time</td>";
                echo "<td><a href='show_chitiethoadon.php?invoice_id=$invoice_id&table=$table&time=$time'><i class='fas fa-eye'></i></a></td>";
                echo "</tr>";

                // Increment the counter for the next invoice
                $invoice_counter++;
            }
            ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
