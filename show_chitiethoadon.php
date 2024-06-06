<?php
// Include Firebase PHP SDK setup
include 'dbconn.php';
$ref_food_prices = 'food'; // Assuming 'food' is the reference path for dish prices

// Fetch food prices from Firebase
$food_prices = $database->getReference($ref_food_prices)->getValue();
// Get invoice_id, table, and time from URL parameters
if (isset($_GET['invoice_id']) && isset($_GET['table']) && isset($_GET['time'])) {
    $invoice_id = $_GET['invoice_id'];
    $table = $_GET['table'];
    $table_number = preg_replace('/\D/', '', $table);
    $time = $_GET['time'];

    // Assuming your Firebase structure allows fetching details by invoice_id, table, and time
    // Query Firebase or other data source to get the specific order details
    $ref_audio = 'food_details';
    $specific_order = $database->getReference($ref_audio)->getChild($table . '-' . $invoice_id . '-' . $time)->getValue();

    if ($specific_order) {
        // Initialize total price variable
        $total_bill = 0;
        ?>
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Chi tiết hóa đơn</title>
            <link rel="stylesheet" href="hoadon.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        </head>
        <body>
        <div class="navbar">
            <?php include 'nav_bar.php'; ?>
        </div>
        <div class="container">
            <h2>Chi tiết hóa đơn</h2>
            <h3>Mã hóa đơn: <?php echo $invoice_id; ?></h3>
            <h3>Bàn: <?php echo $table_number; ?></h3>
            <h3>Thời gian: <?php echo $time; ?></h3>

            <!-- Display the details of the order in a table -->
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                    <tr>
                        <th>STT</th>
                        <th>Tên món ăn</th>
                        <th>Số lượng</th>
                        <th>Đơn giá</th>
                        <th>Thành tiền</th>
                    </tr>
                    </thead>
                    <tbody>
                    <?php
                    // Iterate through each detail of the specific order
                    $counter = 1;
                    foreach ($specific_order as $detail_key => $detail_value) {
                        if (strpos($detail_key, 'details') === 0) {
                            // Extract quantity and dish name from the detail value
                            $split_details = explode(' ', $detail_value, 2);
                            $quantity = trim($split_details[0]);
                            $dish_name = trim($split_details[1]);

                            // Fetch the price for the current dish from the food prices data
                            $unit_price = isset($food_prices[$dish_name]) ? $food_prices[$dish_name] : 0;

                            // Calculate the total price for the current item
                            $total_price = $unit_price * $quantity;

                            // Display the item details in a table row
                            echo "<tr>";
                            echo "<td>$counter</td>";
                            echo "<td>$dish_name</td>";
                            echo "<td>$quantity</td>";
                            echo "<td>$unit_price</td>";
                            echo "<td>$total_price</td>";
                            echo "</tr>";

                            // Increment the total bill with the current item's total price
                            $total_bill += $total_price;

                            // Increment the counter for the next item
                            $counter++;
                        }
                    }
                    ?>
                    </tbody>
                </table>
            </div>

            <!-- Display total bill -->
            <div class="total_container">
                <h3>Tổng thanh toán: </h3>
                <span id="total-price"><?php echo number_format($total_bill); ?> VNĐ</span>
            </div>
        </div>
        </body>
        </html>
        <?php
    } else {
        echo "Không tìm thấy chi tiết hóa đơn cho bàn $table, mã hóa đơn $invoice_id và thời gian $time";
    }
} else {
    echo "Thiếu thông tin truy vấn (invoice_id, table, time)";
}
?>
