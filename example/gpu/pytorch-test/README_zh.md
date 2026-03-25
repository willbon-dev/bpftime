# 如何使用 pytorch 进行测试

## 获取 pytorch
```
git clone --recursive https://github.com/pytorch/pytorch
```

## 编译带有 PTX 的 pytorch
```
uv venv
source ./.venv/bin/activate
uv pip install --group dev
uv pip install mkl-static mkl-include
USE_NCCL=0 USE_MPI=0 TORCH_CUDA_ARCH_LIST=6.1+PTX USE_XPU=0 USE_ROCM=0 REL_WITH_DEB_INFO=1 CMAKE_POLICY_VERSION_MINIMUM=3.5 CUDA_HOME=/usr/local/cuda-12.6 uv pip install --no-build-isolation -v -e .
```

## 运行 pytorch

将下面的程序保存为 `pytorch_test.py`

```python
import torch

data = torch.randint(0, 1000, (10,), dtype=torch.int32, device='cuda')

sorted_data = torch.sort(data)

print(f"Original: {data[:10]}")
print(f"Sorted: {sorted_data.values[:10]}")

```

在终端 1 中，在本目录运行 `bpftime load ./threadhist`

在终端 2 中运行 `bpftime start python pytorch_test.py`（必须在前面创建的 uv venv 中执行）
