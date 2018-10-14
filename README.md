# Quick install
```sh
sudo apt-get update
sudo apt-get upgrade

sudo apt-get remove x264 libx264-dev

sudo apt-get install build-essential checkinstall cmake pkg-config yasm
sudo apt-get install git gfortran
sudo apt-get install libjpeg8-dev libjasper-dev libpng12-dev
sudo apt-get install libtiff5-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev
sudo apt-get install libxine2-dev libv4l-dev
sudo apt-get install libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev
sudo apt-get install qt5-default libgtk2.0-dev libtbb-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install libfaac-dev libmp3lame-dev libtheora-dev
sudo apt-get install libvorbis-dev libxvidcore-dev
sudo apt-get install libopencore-amrnb-dev libopencore-amrwb-dev
sudo apt-get install x264 v4l-utils

sudo apt-get install python-dev python-pip python3-dev python3-pip

sudo apt install redis-server
sudo pip3 install -r requirements.txt

wget https://www.apachefriends.org/xampp-files/5.6.20/xampp-linux-x64-5.6.20-0-installer.run
sudo su
chmod +x xampp-linux-x64-5.6.20-0-installer.run
./xampp-linux-x64-5.6.20-0-installer.run
```

# Requirements
Tương thích với python 3.5
Cài đặt tensorflow (hoặc tensorflow-gpu nếu máy bạn có GPU)
```sh
pip3 install tensorflow
```
hoặc tensorflow-gpu nếu máy bạn có GPU
```sh
pip3 install tensorflow-gpu
```
Cài đặt opencv để hỗ trợ việc hiển thị ảnh
```sh
pip3 install opencv-python opencv-contrib-python
```
Cài đặt các thư viện hỗ trợ tính toán
```sh
pip3 install numpy scipy scikit-learn
```

# Running
Chương trình hỗ trợ 2 chế độ: trực tiếp từ webcam hoặc stream từ IP Camera
#### Khởi động redis-server
Chạy command sau trên terminal:
redis-server
#### Khởi động database mySQL
#### Khởi động services
Chạy các command sau trong các terminal riêng biệt:
python start_service.py -master
python start_service.py -detect
python start_service.py -iden
Đợi cho tất cả các services đã hiện thông báo " ... is running" là có thể khởi động được client
#### Webcam
```sh
python3 start_service.py -client
```
#### IP Webcam
Vào database sửa lại hoặc thêm record trong bảng camera, điền httpUrl hoặc rstpURL
Chạy chương trình bằng lệnh sau
```sh
python3 start_service.py -client -camid x
với x là idCamera trong bảng camera trong database
```

# Training online
Chương trình cung cấp tính năng cho phép người dùng training online mặt người mới trong lúc chương trình đang chạy.  
Ấn **Space**, idCode hiện ra để nhập thông tin số chứng minh nhân dân, sau đó bảng thông tin hiện ra để điền các thông tin người train, 1 khung hình bao đỏ sẽ hiện lên ở phía phải màn hình, người cần training đưa mặt vào vùng này. Ấn **Space** lần nữa để bắt đầu training.  
Thời gian training là **2s**. Trong khoảng thời gian training, người dùng có thể quay mặt đi 1 chút để mô hình dự đoán chính xác hơn
