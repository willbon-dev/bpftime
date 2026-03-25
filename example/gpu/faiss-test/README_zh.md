# 使用 faiss 进行测试的方法

## 获取 faiss 并启用 GPU 支持构建
```
git clone --recursive https://github.com/facebookresearch/faiss

cd faiss
# 注意：
# - 根据你的 CUDA 安装路径和版本，调整 `-DCUDAToolkit_ROOT=/usr/local/cuda-12.6`。
# - 根据你的 GPU 架构设置 `-DCMAKE_CUDA_ARCHITECTURES="61"`：
#     61 = Pascal, 75 = Turing, 80 = Ampere, 89 = Ada, 等。
cmake -DCMAKE_BUILD_TYPE=Debug -DFAISS_ENABLE_GPU=ON -DCUDAToolkit_ROOT=/usr/local/cuda-12.6 -DCMAKE_CUDA_ARCHITECTURES="61" -DFAISS_ENABLE_ROCM=OFF -S . -B build -G Ninja
cmake --build build --config Debug --target demo_ivfpq_indexing_gpu

```

## 运行 bpftime

- 终端 1，在 `example/gpu/faiss-test` 目录中运行：`bpftime load ./threadhist`
- 终端 2，在 `faiss` 目录中运行：`bpftime start ./build/faiss/gpu/test/demo_ivfpq_indexing_gpu`

## 结果

来自 syscall server：
```
16:01:39 
Thread 0: 236
Thread 1: 236
Thread 2: 236
Thread 3: 236
Thread 4: 236
Thread 5: 236
Thread 6: 236
```
