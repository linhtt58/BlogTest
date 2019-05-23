# BlogTest
Thực hiện bài test GotIt
Project gồm 3 folder:
- src: Chứa các file python source code và file cài đặt, chạy chương trình
- document: Chứa thông tin các api và thông tin cơ sở dữ liệu
- database: Chứa file blogtest.sql để tạo các bảng trong cơ sở dữ liệu Mysql
Project được thực hiện trên môi trường Windows
Cài đặt:
Bước 1: Thực hiện cài đặt database
Thực hiện tạo 1 database Mysql với các thông số sau:
- Tên DB: mydb
- User: root
- Pass: 123456789
- host: localhost
Sau đó, thực hiện import file tạo các bảng dữ liệu trong database/blogtest.sql

Bước 2: Thực hiện cài đặt phần mềm.
- Trỏ command line vào thư mục src. Chạy lệnh
pip install -r requirements.txt
pip install Flask-OAuthlib
pip install mysql-connector-python
- Sau khi chạy xong, để chạy ứng dụng, thực hiện lệnh: 
run.bat

Bước 3: Đường dẫn được khởi tạo: 
http://localhost:5000
Thực hiện thêm các đường dẫn RestFul API trong document/Api.xlsx để test
