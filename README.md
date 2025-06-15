Hallo guys sebelum kita jalankan uji coba kita pastikan instal berikut 
1. dlib
2. mysql ( sudo apt update && sudo apt upgrade -y
, sudo apt install mysql-server -y , sudo mysql_secure_installation , sudo systemctl status mysql, sudo mysql -u root -p , mysql --version ) tambahkan semua kode di mylab_backup.sql
3. install python ( sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential libssl-dev zlib1g-dev \
libncurses5-dev libbz2-dev libreadline-dev libsqlite3-dev \
wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev \
libxmlsec1-dev libffi-dev liblzma-dev, cd /usr/src
sudo wget https://www.python.org/ftp/python/3.6.15/Python-3.6.15.tgz
sudo tar xzf Python-3.6.15.tgz
cd Python-3.6.15, sudo ./configure --enable-optimizations
sudo make -j$(nproc)   # Kompilasi dengan semua core CPU
sudo make altinstall   # Pakai altinstall biar gak ganggu python default, python3.6 --version , sudo apt install -y python3.6-venv
python3.6 -m ensurepip --upgrade
 ) atau lewat https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe
   4. install pip C:\Users\asamu>pip list
Package                 Version
----------------------- -----------
autopep8                2.0.4
Brotli                  1.1.0
certifi                 2025.4.26
click                   8.0.4
cmake                   3.28.4
colorama                0.4.5
cycler                  0.11.0
dlib                    19.8.1
face-recognition        1.2.3
face-recognition-models 0.3.0
importlib-metadata      4.8.3
kiwisolver              1.3.1
matplotlib              3.3.4
mutagen                 1.45.1
mysql-connector-python  8.0.17
numpy                   1.19.5
opencv-python           4.2.0.34
Pillow                  8.4.0
pip                     21.3.1
playsound               1.2.2
protobuf                3.19.6
pycodestyle             2.10.0
pycryptodomex           3.21.0
pyparsing               3.1.4
python-dateutil         2.9.0.post0
setuptools              40.6.2
six                     1.17.0
tomli                   1.2.3
typing_extensions       4.1.1
websockets              9.1
yt-dlp                  2022.7.18
zipp                    3.6.0

C:\Users\asamu>
   

