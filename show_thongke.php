<?php
require __DIR__ . '/vendor/autoload.php';

use Kreait\Firebase\Factory;

$factory = (new Factory)
    ->withServiceAccount('pbl5-nhom7-firebase-adminsdk-9fxho-3b31c6d79d.json')
    ->withDatabaseUri('https://pbl5-nhom7-default-rtdb.asia-southeast1.firebasedatabase.app/');

$database = $factory->createDatabase();

$ref_orders = 'food_details'; // Điều chỉnh đường dẫn này tùy theo cấu trúc Firebase của bạn
$orders = $database->getReference($ref_orders)->getValue();

$dish_counts = [];
$dish_counts_today = [];
$date_today = date("d:m:Y");

$revenue_by_day = [];
$revenue_by_month = [];
$revenue_by_year = [];
$total_revenue = 0; // Khởi tạo biến total_revenue

$products = [
    'bánh bèo' => 10000,
    'bún bò' => 35000,
    'chè' => 20000,
    'cơm gà' => 55000,
    'cơm hến' => 25000,
    'gà quay' => 50000,
    'mỳ quảng' => 30000,
    'mỳ ý' => 35000,
    'nước cam' => 20000
];

if ($orders) {
    foreach ($orders as $order_key => $order) {
        // Kiểm tra và phân tích ngày tháng năm
        list($day, $month, $year) = explode(":", $order_key);

        foreach ($order as $key => $value) {
            if (strpos($key, 'details') !== false) {
                if (is_string($value)) {
                    $details = explode(' ', $value, 2);
                    if (count($details) < 2) {
                        continue; // Bỏ qua nếu không có đủ 2 phần tử
                    }
                    $quantity = (int)$details[0];
                    $dish_name = $details[1];

                    $price = isset($products[$dish_name]) ? $products[$dish_name] : 0;
                    $revenue = $quantity * $price;

                    // Tính doanh thu theo ngày
                    $date = "$day:$month:$year";
                    if (!isset($revenue_by_day[$date])) {
                        $revenue_by_day[$date] = 0;
                    }
                    $revenue_by_day[$date] += $revenue;

                    // Tính doanh thu theo tháng
                    $month_year = "$month:$year";
                    if (!isset($revenue_by_month[$month_year])) {
                        $revenue_by_month[$month_year] = 0;
                    }
                    $revenue_by_month[$month_year] += $revenue;

                    // Tính doanh thu theo năm
                    if (!isset($revenue_by_year[$year])) {
                        $revenue_by_year[$year] = 0;
                    }
                    $revenue_by_year[$year] += $revenue;

                    // Tổng doanh thu
                    $total_revenue += $revenue;
                }
            }
        }
    }

    ksort($revenue_by_day);
    ksort($revenue_by_month);
    ksort($revenue_by_year);
}

$dish_counts = [];

if ($orders) {
    foreach ($orders as $order_key => $order) {
        foreach ($order as $key => $value) {
            if (strpos($key, 'details') !== false) {
                if (is_string($value)) {
                    $details = explode(' ', $value, 2);
                    if (count($details) < 2) {
                        continue; // Bỏ qua nếu không có đủ 2 phần tử
                    }
                    $quantity = (int)$details[0];
                    $dish_name = $details[1];

                    // Tính toàn bộ số lượng của mỗi món ăn
                    if (!isset($dish_counts[$dish_name])) {
                        $dish_counts[$dish_name] = 0;
                    }
                    $dish_counts[$dish_name] += $quantity;
                }
            }
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sales Statistics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f8f9fa;
        color: #343a40;
        margin: 0;
        padding: 0;
    }
    .main_info {
        display: flex;
        justify-content: space-between;
        margin: 10px auto;
        max-width: 1400px; /* Điều chỉnh kích thước tối đa của trang */
    }
    .main__information-detail,
    .main__information-horizontal-chart {
        flex-grow: 1;
        margin-right: 20px; /* Khoảng cách giữa hai phần */
    }
    .main__information-detail {
        padding: 30px;
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-width: 100%; /* Phóng to chiều rộng của phần tử */
    }
    .main__information-horizontal-chart {
        padding: 30px;
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-width: 100%; /* Phóng to chiều rộng của phần tử */
    }
    .main__table-form {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .select__form, .form__end {
        display: flex;
        align-items: center;
    }
    .form-group {
        display: flex;
        align-items: center;
        margin-bottom: 0;
    }
    .form__comboBox select, .datetime input[type="date"] {
        margin-left: 10px;
        padding: 5px 10px;
        border: 1px solid #ced4da;
        border-radius: 4px;
    }
    .form__end .form-group2 {
        margin-left: 20px;
    }
    .column__info-total {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .column__total-profit, .column__info-details {
        text-align: center;
        flex-grow: 1;
    }
    .column__total-profit p, .column__info-details p {
        margin: 5px 0;
    }
    .columns__chart {
        margin-top: 20px;
    }
    .total__amount, .total__amount-revenue {
        font-size: 1.2em;
        font-weight: bold;
    }
    .total__money-amount, .total__money-revenue {
        font-size: 1.5em;
        color: #007bff;
    }
</style>

</head>
<body>
    <div class="navbar">
      <?php include 'nav_bar.php'; ?>
    </div>
    <div class="main_info">
    <div class="main__information-detail">
        <div class="main__table-form">
            <div class="select__form">
                <div class="form-group">
                    <label class="control-label"> Thống kê: </label>
                    <div class="form__comboBox">
                        <form method="post">
                            <select name="combobox_Item" id="date-select">
                                <option value="day" selected> Theo ngày</option>
                                <option value="month"> Theo tháng</option>
                                <option value="year"> Theo năm</option>
                            </select>
                        </form>
                    </div>
                </div>
            </div>
            <div class="form__end datetime">
                <div class="form-group">
                    <form method="get" action="">
                        <label class="control-label">Từ:</label>
                        <input type="date" name="fromDate" onchange="updateChart()">
                    </form>
                </div>
                <div class="form-group2">
                    <form method="get" action="">
                        <label class="control-label">Đến:</label>
                        <input type="date" name="toDate" onchange="updateChart()">
                    </form>
                </div>
            </div>
        </div>
        <div class="infor__details">
            <div class="column__info-details">
                <div class="columns__chart">
                    <p class="total__amount-revenue"> Tổng doanh thu</p>
                    <p class="total__money-revenue"> <?php echo number_format($total_revenue, 0, ',', '.') . ' VNĐ'; ?></p>
                    <canvas id="revenueChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    <div class="main__information-horizontal-chart ">
        
    </div>
    </div>
    <div class="main__information-vertical-chart">
        <canvas id="topSellingItemsChart"></canvas>
    </div>
    
</body>
</html>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        const revenueByDay = <?php echo json_encode($revenue_by_day); ?>;
        const revenueByMonth = <?php echo json_encode($revenue_by_month); ?>;
        const revenueByYear = <?php echo json_encode($revenue_by_year); ?>;

        const ctx = document.getElementById('revenueChart').getContext('2d');

        const labelsDay = Object.keys(revenueByDay);
        const dataDay = Object.values(revenueByDay);
        const labelsMonth = Object.keys(revenueByMonth);
        const dataMonth = Object.values(revenueByMonth);
        const labelsYear = Object.keys(revenueByYear);
        const dataYear = Object.values(revenueByYear);

        let currentChart;

        const createChart = (labels, data) => {
            if (currentChart) {
                currentChart.destroy();
            }
            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Revenue',
                        data: data,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        fill: true
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        };

        const updateChart = () => {
            const fromDate = document.getElementsByName('fromDate')[0].value;
            const toDate = document.getElementsByName('toDate')[0].value;
            let selectedOption = document.getElementById('date-select').value;

            let labels, data;

            switch (selectedOption) {
                case 'day':
                    labels = [];
                    data = [];
                    let currentDate = new Date(fromDate);
                    const endDate = new Date(toDate);
                    if (!fromDate || !toDate) {
                        for (const [key, value] of Object.entries(revenueByDay)) {
                            const [day, month, year] = key.split(':');
                            const formattedDate = `${day}/${month}/${year}`;
                            labels.push(formattedDate);
                            data.push(value);
                        }
                    } else {
                        while (currentDate <= endDate) {
                            const formattedDate = currentDate.toLocaleDateString('en-GB');
                            labels.push(formattedDate);

                            const formattedKey = currentDate.getDate() + ':' + (currentDate.getMonth() + 1) + ':' + currentDate.getFullYear();
                            data.push(revenueByDay[formattedKey] || 0);

                            currentDate.setDate(currentDate.getDate() + 1);
                        }
                    }
                    createChart(labels, data);
                    break;
                case 'month':
                    selectedOption = 'day'; // Update to 'day' to reuse logic for day selection
                case 'year':
                    labels = Object.keys(selectedOption === 'month' ? revenueByMonth : revenueByYear);
                    data = Object.values(selectedOption === 'month' ? revenueByMonth : revenueByYear);
                    createChart(labels, data);
                    break;
                default:
                    alert('Invalid selection');
            }
        };

        document.getElementById('date-select').addEventListener('change', updateChart);

        updateChart(); // Initialize with the default selected option

        // Chuyển đổi $dish_counts thành mảng các cặp key-value
        const dishCountsArray = Object.entries(<?php echo json_encode($dish_counts); ?>);

        // Sắp xếp mảng theo số lượng giảm dần
        const sortedDishCounts = dishCountsArray.sort((a, b) => b[1] - a[1]);
        // Tạo mảng chứa tên các món ăn và số lượng tương ứng
        const labelsTop5 = sortedDishCounts.map(dish => dish[0]);
        const dataTop5 = sortedDishCounts.map(dish => dish[1]);

        // Tạo biểu đồ cột cho 5 món ăn bán chạy nhất
        const config = {
            type: 'bar',
            data: {
                labels: labelsTop5,
                datasets: [{
                    label: 'Số lượng bán ra',
                    data: dataTop5,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    title: {
                        display: true,
                        text: 'Top 5 món ăn bán chạy nhất',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        };

        // Vẽ biểu đồ
        const ctxTop5 = document.getElementById('topSellingItemsChart').getContext('2d');
        new Chart(ctxTop5, config);

    });

</script>

