<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Our Restaurant</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css" />
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            background-image: url('background.jpg');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        .navbar {
            /* Ensure the navbar has some styling if needed */
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 600;
        }
        
        p {
            color: #555;
            line-height: 1.7;
            font-size: 1.1em;
            text-align: justify;
            margin-bottom: 18px;
        }

        .loi_ngo {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 50px;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }

        .loi_ngo img {
            width: 100%;
            max-width: 300px;
            height: auto;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        .loingo_child {
            max-width: 800px;
            text-align: center;
        }

        .loingo_child h1 {
            color: #333;
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .loingo_child p {
            color: #555;
            font-size: 1.1em;
            line-height: 1.8;
            margin-bottom: 15px;
        }

        @media (min-width: 768px) {
            .loi_ngo {
                flex-direction: row;
                justify-content: center;
                text-align: left;
            }

            .loi_ngo img {
                margin-right: 20px;
                margin-bottom: 0;
            }
        }

        footer {
            background-color: #333;
            color: white;
            padding: 20px 0;
            text-align: center;
        }

        footer .social-icons {
            margin: 10px 0;
        }

        footer .social-icons a {
            color: white;
            margin: 0 10px;
            text-decoration: none;
            font-size: 1.2em;
        }

        footer .social-icons a:hover {
            color: #ddd;
        }

        footer p {
            margin: 5px 0;
            font-size: 1em;
        }
    </style>
</head>
<body>

    <div class="navbar">
        <?php include 'nav_bar.php'; ?>
    </div>

    <div class="container">
        <div class="introduction">
            <img src="img/home-vi-min.jpg" alt="Restaurant Image">
        </div>
        <div class="loi_ngo">
            <img src="img/loingo-min.png" alt="Loi Ngo">
            <div class="loingo_child">
                <h1>Lời Ngỏ</h1>
                <p>Chúng tôi rất vinh dự được phục vụ quý khách tại nhà hàng của chúng tôi. Với một menu thay đổi theo mùa, chúng tôi tập trung vào nguyên liệu tươi, được cung cấp địa phương, các món ăn sáng tạo và sự kết hợp độc đáo của hương vị.</p>
                <p>Không gian ấm áp và thân thiện của chúng tôi là lý tưởng cho bất kỳ dịp nào, cho dù bạn đang ăn tối gia đình, một buổi hẹn lãng mạn hoặc một bữa ăn bình dân với bạn bè. Nhân viên chúng tôi chu đáo và thân thiện cam kết mang đến cho bạn một trải nghiệm ăn uống xuất sắc.</p>
                <p>Chúng tôi rất mong được chào đón bạn và tạo ra một trải nghiệm ăn uống đáng nhớ cho bạn!</p>
            </div>
        </div>
    </div>

    <footer>
        <div class="social-icons">
            <a href="#"><i class="fab fa-facebook-f"></i></a>
            <a href="#"><i class="fab fa-twitter"></i></a>
            <a href="#"><i class="fab fa-instagram"></i></a>
            <a href="#"><i class="fab fa-linkedin-in"></i></a>
        </div>
        <p>&copy; 2024 Our Restaurant. All rights reserved.</p>
        <p>Contact us: (123) 456-7890 | email@example.com</p>
    </footer>

    <script>
    </script>

</body>
</html>
