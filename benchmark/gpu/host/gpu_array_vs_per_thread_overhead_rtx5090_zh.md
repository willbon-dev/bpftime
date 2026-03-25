# GPU Array 与 Per-Thread GPU Array 的主机侧开销对比

本文档对比两种主机侧 map 基准测试：

- `gpu_array_map_host_perf`：`BPF_MAP_TYPE_GPU_ARRAY_MAP`
- `gpu_per_thread_array_map_host_perf`：`BPF_MAP_TYPE_PERGPUTD_ARRAY_MAP`

每次对比都保持每个 key 的有效字节数一致：

- 普通 GPU array map：`value_size = per_thread_value_size * thread_count`
- PERGPUTD array map：`value_size = per_thread_value_size`，并显式设置 `thread_count`

设备：`NVIDIA GeForce RTX 5090`
每次运行迭代数：`50000`
最大条目数：`1024`
每线程值大小：`8` 字节
GDRCopy 驱动可用性：`no`

由于这台机器上没有 `/dev/gdrdrv`，这些数字代表回退到 `cuMemcpyDtoH` 路径的结果。
这个对比并不直接隔离名为 `shared_array_map` 的 runtime 路径。

| thread_count | effective bytes/key | gpu_array update ns/op | per_thread update ns/op | update ratio | gpu_array lookup ns/op | per_thread lookup ns/op | lookup ratio |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | 256 | 3835.9 | 3832.8 | 0.999x | 4865.1 | 4835.0 | 0.994x |
| 128 | 1024 | 3855.5 | 3851.5 | 0.999x | 4905.0 | 4866.6 | 0.992x |
| 256 | 2048 | 3903.6 | 3911.0 | 1.002x | 5044.1 | 5084.2 | 1.008x |
| 1024 | 8192 | 4325.8 | 4327.6 | 1.000x | 5843.0 | 5896.6 | 1.009x |

## 解读

- 在 `NVIDIA GeForce RTX 5090` 上，当按相同每 key 字节数归一化后，PERGPUTD 主机侧更新路径与普通 GPU array map 基本持平。
- lookup 在所有测试的线程数下也保持在相近区间。
- 这个基准只衡量主机侧 `update`/`lookup` 开销，不包括内核 helper 的开销或 GPU 侧争用。

## 复现

构建基准：

```bash
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DBPFTIME_ENABLE_CUDA_ATTACH=ON \
  -DBPFTIME_CUDA_ROOT=/usr/local/cuda \
  -DBPFTIME_ENABLE_GDRCOPY=ON

cmake --build build -j --target gpu_array_map_host_perf gpu_per_thread_array_map_host_perf
```

生成该报告：

```bash
python3 benchmark/gpu/host/measure_gpu_array_vs_per_thread_overhead.py \
  --build-dir build \
  --output benchmark/gpu/host/gpu_array_vs_per_thread_overhead_rtx5090.md
```
