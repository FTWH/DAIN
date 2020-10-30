## Simple
apt update
apt install -y wget
apt install -y python3-pip
ln -s /usr/bin/python3 /usr/bin/python

## Follow Colab
pip3 install --upgrade pip
pip3 install torch==1.4.0+cu100 torchvision==0.5.0+cu100 -f https://download.pytorch.org/whl/torch_stable.html

pip3 install scipy==1.1.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

apt install -y git
git clone https://github.com/FTWH/DAIN /content/DAIN

cd /content/DAIN/my_package/
./build.sh

cd ../PWCNet/correlation_package_pytorch1_0
./build.sh

cd /content/DAIN/
mkdir model_weights

cd model_weights
wget https://dain-env-1301537901.cos.ap-guangzhou.myqcloud.com/best.pth

apt-get install -y imagemagick imagemagick-doc
pip3 install scikit-build -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install opencv-python opencv-contrib-python -i https://pypi.mirrors.ustc.edu.cn/simple

apt install -y ffmpeg
apt install -y zip
pip3 install imageio -i https://pypi.tuna.tsinghua.edu.cn/simple