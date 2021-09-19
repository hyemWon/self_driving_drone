## Alpha-Pose Implements Code
https://github.com/MVIG-SJTU/AlphaPose
### Prerequisites
```
Nvidia device with CUDA, example for Ubuntu 20.04 (if you have no nvidia device, delete this line from setup.py
Python 3.5+
Cython
PyTorch 1.1+, for users with PyTorch 1.5 and 1.5+, please merge the pull request #592 by: git pull origin pull/592/head
torchvision 0.3.0+
numpy
python-package setuptools >= 40.0, reported by this issue
Linux, Windows user check here
```

### Install with pip
```
1. Install PyTorch  
pip3 install torch==1.1.0 torchvision==0.3.0  
# Check torch environment by:  python3 -m torch.utils.collect_env

# 2. Get AlphaPose
git clone https://github.com/MVIG-SJTU/AlphaPose.git
# git pull origin pull/592/head if you use PyTorch>=1.5
cd AlphaPose

# 3. install
export PATH=/usr/local/cuda/bin/:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64/:$LD_LIBRARY_PATH
pip install cython
sudo apt-get install libyaml-dev
python3 setup.py build develop --user
```
### Run Codes
* predict >> inference.py