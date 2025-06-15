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
   

