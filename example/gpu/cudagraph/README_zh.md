# CUDA Graph eBPF Probe 示例

这个示例展示了 bpftime 如何对通过 CUDA Graph 执行的 kernel 进行 instrumentation。

- CUDA 应用 `vec_add_graph` 会构建一个包含 `vectorAdd` kernel 的 CUDA Graph，并通过 `cudaGraphLaunch` 反复启动它。
- eBPF 程序 `cuda_probe` 会挂载到 `vectorAdd` kernel 的入口/退出点，即使这个 kernel 是从 graph 中启动的。

## 构建

从 `bpftime/` 仓库根目录开始，先启用 CUDA attach 构建 bpftime：

```bash
cmake -Bbuild -DBPFTIME_ENABLE_CUDA_ATTACH=1 -DBPFTIME_CUDA_ROOT=/usr/local/cuda .
cmake --build build -j"$(nproc)"
```

构建示例：

```bash
# 或者：export PATH=$BPFTIME_CUDA_ROOT/bin:$PATH
make -C example/gpu/cudagraph
```

## 运行

打开两个终端。

**终端 1（server，加载 eBPF 程序）：**

```bash
BPFTIME_LOG_OUTPUT=console BPFTIME_GLOBAL_SHM_NAME=bpftime_maps_shm_graph \
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
  example/gpu/cudagraph/cuda_probe
```

**终端 2（client，运行 CUDA Graph 应用）：**

```bash
BPFTIME_LOG_OUTPUT=console BPFTIME_GLOBAL_SHM_NAME=bpftime_maps_shm_graph \
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  example/gpu/cudagraph/vec_add_graph
```

这样就会打印出来自 `cuda_probe` 的 eBPF 输出，确认 graph 启动的 kernel 已被跟踪。
