<?php
require __DIR__ . '/vendor/autoload.php';

use Kreait\Firebase\Factory;

// Khởi tạo factory với tài khoản dịch vụ và URI cơ sở dữ liệu
$factory = (new Factory)
    ->withServiceAccount('pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json')
    ->withDatabaseUri('https://pbl5-nhom7-default-rtdb.asia-southeast1.firebasedatabase.app/');

// Tạo một thể hiện của Cơ sở dữ liệu Firebase Realtime trực tiếp từ factory
$database = $factory->createDatabase();

// Hàm xử lý hoàn tất đặt hàng cho bàn
function handleTableCompletion($database, $table_name) {
    $new_details = getVoiceInputAsText($database);
    if (!empty($new_details)) {
        $bill_id = uniqid(); // Tạo một ID hóa đơn duy nhất
        $time_now = date('H:i:s d:m:Y'); // Lấy thời gian hiện tại - Định dạng YYYY-MM-DD HH:MM:SS
        $order_identifier = 'Ban' . substr($table_name, 3) . '-' . $bill_id . '-' . $time_now;

        // Khởi tạo cấu trúc dữ liệu mới cho thông tin món ăn dưới dạng một mảng từ thông tin thu được
        $itemDetails = [];
        foreach ($new_details as $index => $detail) {
            $indexNumber = $index + 1; // Tạo chỉ số bắt đầu từ 1
            // Sử dụng cú pháp "detailsX" để lưu từng món ăn (ví dụ: "details1", "details2")
            $itemDetails["details$indexNumber"] = $detail;
        }

        // Kiểm tra xem đã có đơn hàng cho bàn chưa
        $existing_order_details = $database->getReference('food_details/' . $order_identifier)->getValue();
        if (!$existing_order_details) {
            // Thêm chi tiết mới với cấu trúc đã được chỉnh sửa
            $database->getReference('food_details/' . $order_identifier)->set($itemDetails);
            echo "Bàn $table_name đã được gọi món!";
        } else {
            echo "Đã tồn tại một đơn hàng cho bàn $table_name. Không thể tạo đơn hàng mới hoàn toàn.";
        }
    } else {
        echo "Không có dữ liệu hợp lệ để thêm!";
    }
}

function getVoiceInputAsText($database) {
    // Lấy dữ liệu mới nhất từ 'data_temp'
    $latest_data_temp = $database->getReference('data_temp')->orderByKey()->limitToLast(1)->getValue();
    $latest_menu = [];
    
    if (!empty($latest_data_temp)) {
        // Khi 'data_temp' có dữ liệu, lấp đầy 'latest_menu' với các giá trị của menu
        $latest_data_temp_array = array_pop($latest_data_temp); // Lấy phần tử cuối cùng của mảng
        foreach ($latest_data_temp_array as $key => $value) {
            foreach ($value as $menu_item) {
                $latest_menu[] = $menu_item;
            }
        }
    }
    
    return $latest_menu;
}

if (isset($_POST['table_name'])) {
    $selected_table_name = $_POST['table_name'];

    $selected_table_ref = $database->getReference('tables/' . $selected_table_name);
    $selected_table_status = $selected_table_ref->getChild('status')->getValue() ?? 0;

    $all_tables_ref = $database->getReference('tables');
    $all_tables = $all_tables_ref->getValue();
    foreach ($all_tables as $table_name => $table_data) {
        if ($table_data['status'] == 1) {
            handleTableCompletion($database, $table_name);
        }
    }

    $new_status = ($selected_table_status + 1) % 3;

    // Set the new status for the selected table
    $selected_table_ref->getChild('status')->set($new_status);

    // If the new status is 1, reset other tables' statuses
    if ($new_status == 1) {
        foreach ($all_tables as $table_name => $table_data) {
            if ($table_name !== $selected_table_name && $table_data['status'] != 0) {
                $database->getReference('tables/' . $table_name . '/status')->set(0);
            }
        }
    }

    // Immediately change the status from 2 to 0
    if ($new_status == 2) {
        $selected_table_ref->getChild('status')->set(0);
        echo "Cập nhật trạng thái của bàn $selected_table_name từ 2 sang 0 thành công!";
    } else {
        echo "Cập nhật trạng thái của bàn $selected_table_name từ $selected_table_status sang $new_status thành công!";
    }
}
?>
