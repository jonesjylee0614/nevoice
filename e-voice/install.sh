conda create -n evoice python=3.12

pip install --upgrade pip setuptools wheel

# debian
sudo apt install -y portaudio19-dev

# centos
#sudo yum install -y portaudio-devel

# mac
#brew install portaudio

pip install pyaudio
pip install -r requirements.txt
