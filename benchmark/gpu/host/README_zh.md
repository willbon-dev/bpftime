# 主机侧 GPU Map 微基准

本目录包含 bpftime CUDA 后端 map 的**主机侧**微基准测试。

## 前置条件

- 可用的 CUDA 驱动 + 工具包（CUDA 头文件 + `libcuda.so`）
- 启用 CUDA attach 的 bpftime 构建
- 可选（用于获得 GDRCopy 加速）：安装 GDRCopy 用户库（`libgdrapi.so`）并加载 `gdrdrv`（会创建 `/dev/gdrdrv`）

## 构建

在仓库根目录下执行：

```bash
cmake -S . -B build -G Ninja \
  -DBPFTIME_ENABLE_CUDA_ATTACH=ON \
  -DBPFTIME_CUDA_ROOT=/usr/local/cuda \
  -DBPFTIME_ENABLE_GDRCOPY=ON

cmake --build build -j --target gpu_array_map_host_perf gpu_per_thread_array_map_host_perf
```

如果你不想启用 GDRCopy 支持，可以去掉 `-DBPFTIME_ENABLE_GDRCOPY=ON`，二进制仍然可以工作，只是 `--gdrcopy 1` 会始终回退到 `cuMemcpyDtoH`。

## 二进制

- `build/benchmark/gpu/host/gpu_array_map_host_perf`
- `build/benchmark/gpu/host/gpu_per_thread_array_map_host_perf`

## `gpu_array_map_host_perf`

基准测试 `BPF_MAP_TYPE_GPU_ARRAY_MAP`（每 key 字节数 = `value_size`）。

```bash
# 基线（cuMemcpyDtoH）
./build/benchmark/gpu/host/gpu_array_map_host_perf \
  --iters 50000 --max-entries 1024 --value-size 8 \
  --gdrcopy 0

# 启用 GDRCopy（混合策略）
./build/benchmark/gpu/host/gpu_array_map_host_perf \
  --iters 50000 --max-entries 1024 --value-size 8 \
  --gdrcopy 1 --gdrcopy-max-per-key-bytes 4096
```

## `gpu_per_thread_array_map_host_perf`

基准测试 `BPF_MAP_TYPE_PERGPUTD_ARRAY_MAP`（每 key 字节数 = `value_size * thread_count`）。

```bash
# 基线（cuMemcpyDtoH）
./build/benchmark/gpu/host/gpu_per_thread_array_map_host_perf \
  --iters 50000 --max-entries 1024 --value-size 8 --thread-count 32 \
  --gdrcopy 0

# 启用 GDRCopy（混合策略）
./build/benchmark/gpu/host/gpu_per_thread_array_map_host_perf \
  --iters 50000 --max-entries 1024 --value-size 8 --thread-count 32 \
  --gdrcopy 1 --gdrcopy-max-per-key-bytes 4096
```

## 参数

- `--gdrcopy 0|1`：启用/禁用 GDRCopy 尝试
- `--gdrcopy-max-per-key-bytes <N>`：当每 key 字节数 `> N` 时跳过 GDRCopy（设为 `0` 可关闭阈值）

说明：

- 如果运行时不可用 GDRCopy（缺少 `libgdrapi.so` 或 `/dev/gdrdrv`），bpftime 会自动回退到 `cuMemcpyDtoH`，性能会与基线一致。

## GPU array 与 per-thread GPU array 主机开销对比

仓库中提供了一个可复现的主机侧对比，用于比较：

- `gpu_array_map_host_perf`，对应 `BPF_MAP_TYPE_GPU_ARRAY_MAP`
- `gpu_per_thread_array_map_host_perf`，对应 `BPF_MAP_TYPE_PERGPUTD_ARRAY_MAP`

这对理解两种主机侧 map 实现的相对 `update`/`lookup` 成本很有帮助，前提是按照相同的每 key 有效字节数进行归一化。它并不直接隔离名为 `shared_array_map` 的 runtime 路径。

为了保证对比有意义，两个基准运行时使用相同的每 key 有效字节数：

- 普通 GPU array map：`value_size = per_thread_value_size * thread_count`
- PERGPUTD array map：`value_size = per_thread_value_size`

仓库还包含一个可复现的测量脚本：

```bash
python3 benchmark/gpu/host/measure_gpu_array_vs_per_thread_overhead.py \
  --build-dir build \
  --output benchmark/gpu/host/gpu_array_vs_per_thread_overhead_rtx5090.md
```

该脚本：

- 运行一个固定的线程数矩阵（`32`、`128`、`256`、`1024`）
- 在相同每 key 字节数下比较 update 和 lookup 成本
- 为每次运行分配唯一的 `BPFTIME_GLOBAL_SHM_NAME`，避免重复测量时冲突
- 生成一份可以直接提交到仓库中的 Markdown 报告

RTX 5090 上生成的示例报告已提交在：

- `benchmark/gpu/host/gpu_array_vs_per_thread_overhead_rtx5090_zh.md`
