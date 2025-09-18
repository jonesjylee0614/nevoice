import torch

# 这个版本得是cu1xx才行，表示装的cuda驱动
# 手动安装：https://download.pytorch.org/whl/cu126/torch-2.6.0%2Bcu126-cp312-cp312-win_amd64.whl#sha256=b10c39c83e5d1afd639b5c9f5683b351e97e41390a93f59c59187004a9949924
# pip3 install torch-2.6.0+cu126-cp312-cp312-win_amd64.whl
print(torch.__version__)
print(torch.cuda.is_available())

if torch.cuda.is_available():
    # 指定要使用的 GPU 设备
    torch.cuda.set_device(0)