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
sudo pip3 install -r requirements.txt
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
Chương trình hỗ trợ 2 chế độ: input video trưci tiếp từ Webcam và input video từ ứng dụng IP Webcam trên Android
#### Webcam
```sh
python3 control_panel.py -run
```
#### IP Webcam
Tải app IP Webcam tại https://play.google.com/store/apps/details?id=com.pas.webcam .  
Start server trên ứng dụng, trên màn hình sẽ thấy được IPv4 (VD: http://192.168.0.102:8080).  
Chạy chương trình bằng lệnh sau
```sh
python3 control_panel.py -run --server=http://192.168.0.102:8080/video
```

# Training online
Chương trình cung cấp tính năng cho phép người dùng training online mặt người mới trong lúc chương trình đang chạy.  
Ấn **Space**, 1 khung hình bao đỏ sẽ hiện lên ở phía phải màn hình, người cần training đưa mặt vào vùng này. Ấn **Space** lần nữa để bắt đầu training.  
Thời gian training là **2s**. Trong khoảng thời gian training, người dùng có thể quay mặt đi 1 chút để mô hình dự đoán chính xác hơn

# Config
Lưu trữ trong vision_config.py
#### Database config
* **DATABASE_DIR** : đường dẫn đến thư mục chứa database
* **DATABASE_NAME_LOAD** : tên database lúc load database
* **DATABASE_NAME_SAVE** : tên database lúc save database
* **SAVE_DATABASE** : có 2 lựa chọn True, False. Nếu True thì sau khi training online, database mới sẽ được lưu, nếu là False thì sẽ không lưu.
#### Model config
* **MODEL_DIR** : đường dẫn đến thư mục chứa thuật toán facenet.
* **DETECT_DEVIC**E : tùy chọn thiết bị thực hiện thuật toán detect face, mặc định là ‘auto', chương trình sẽ tự động chọn thiết bị phù hợp nhất, có thể chọn ‘cpu’ hay ‘gpu’.
* **ENCODE_EMBEDD_DEVICE** : tùy chọn thiết bị thực hiện thuật toán verify face, mặc định là auto, có thể thay đổi thành cpu hay gpu.
* **RECOGNITION_PROBABILITY** : xác suất gán nhãn đúng, mỗi mặt input, thuật toán verify sẽ cho ra kết quả là nhãn dán và xác suất đúng, với xác suất thấp hơn
* **RECOGNITION_PROBABILITY** thì mặt sẽ được gán nhãn là ‘Unknown’.
* **DETECT_SCALE** : detect_scale càng lớn chương trình chạy càng nhanh, tuy nhiên càng thiếu chính xác và khoảng cách detect face cũng thấp, ngược lại chương trình chạy càng tốt, detect xa hơn, nhưng nặng hơn, detect scale không nhỏ hơn 1, và là số nguyên.
* **FLIP**: True thì ảnh sẽ quay ngược theo chiều ngang, False thì giữ nguyên ảnh input
* **ENRICH_DATA**: True thì sau khi chụp ảnh để training online, sẽ tự động flip, làm mờ, … để làm giàu dữ liệu người đó lên, tăng độ chính xác khi nhận diện người đó, tuy nhiên nếu dùng quá nhiều, có thể làm mất cân bằng độ lớn với bộ dữ liệu negative, ảnh hưởng đến độ chính xác của chương trình.
#### Screen config
* **POS_COLOR** : màu tích cực, dùng để hiển thị các thông tin tích cực như dự đoán đúng
* **NEG_COLOR** : màu tiêu cực, dùng để hiển thị các thông tin như dự đoán sai
* **THUMB_BOUNDER_COLOR** : màu dùng để vẽ biên cho thumbnail
* **LINE_THICKNESS** : độ dày của nét vẽ
* **FONT_SIZE** : kích thước chữ viết
* **DIS_THUMB_X** : khoảng cách thumbnail đến biên trái ảnh
* **DIS_THUMB_Y** : khoảng các thumbail đến biên trên của ảnh
* **DIS_BETWEEN_THUMBS** : khoảng cách giữa các thumbnail
* **FPS_POS** : vị trí hiển thị FPS
* **SCREEN_SIZE** : kích thước ảnh input, được tự động chỉnh với mỗi input, không cần thiết phải chỉnh tay thông số này.
* **TRAINING_AREA** : kích thước vùng training online, cũng được tự động chỉnh.
* **PADDING**: khoảng cách biên của training online đến biên ảnh
* **SHOW_LOG_PREDICTION**: nếu True, sẽ in ra log thuật toán nhận diện khuôn mặt
* **SHOW_LOG_TRACKING**: nếu True, sẽ in ra log thuật toán tracking.