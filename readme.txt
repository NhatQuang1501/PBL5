# Tên Dự Án
WEB: AI's voice detection 
## Mô tả
Đây là dự án Django web được phát triển để triển khai model AI giúp nhận biết được âm thanh do AI tạo ra .

## Cài Đặt
1. Clone repository này về máy của bạn:
    ```bash
    git clone git@github.com:legacy281/webaivoicedetection.git
    ```
2. Tạo một môi trường ảo và cài đặt các dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Khởi động server phát triển:
    ```bash
    python manage.py runserver
    ```

## Cách Sử Dụng
Tại giao diện demo up file âm thanh định dạng .flac => result => đánh giá

## Cấu Trúc Dự Án
webai/templates/index.html  => giao diện chính
webai/static/script.js => xử lí các sự kiện người dùng
ai/epoch_5_14_veitnamesefinal.pth => model xử lí giọng việt nam 
ai/epoch_14_newbest.pth => model giọng tiếng anh
ai/urls.py => đường dẫn tương ứng với yêu cầu xử lí 
ai/views => chứa các hàm xử lí các yêu cầu
ai/predict.py, ai/predict2.py => file gọi model và xử lí âm thanh để đưa ra kết quả dự đoán

## Tác Giả
legacy281

