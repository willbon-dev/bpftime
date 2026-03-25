# GPU Shared Array Map 示例

这个示例演示了 `BPF_MAP_TYPE_GPU_ARRAY_MAP`（普通、非 per-thread、单副本共享数组）和 `BPF_MAP_TYPE_GPU_HASH_MAP`（普通、非 per-thread、共享 hash map）在用户态与 bpftime 结合时的行为。这个示例依赖 agent 侧进行更新，而 server 只负责读取，不会回写到 HOST。

- **BPF 程序：** `gpu_shared_map.bpf.c` 会在 `kretprobe/vectorAdd` hook 中递增 `key=0`。
- **Host 程序：** `gpu_shared_map.c` 会周期性读取并打印 `counter[0]` 以及 per-thread counter `counter_per_thread[tid]`。
- **CUDA 程序：** `vec_add.cu` 周期性运行，触发 BPF 程序更新 map。

## 前置条件
- 已安装 clang/llvm、make 和 gcc。
- 可用的 CUDA 环境（`nvcc`、`libcudart`）可访问，并且有 GPU。
- 仓库子模块 `third_party/libbpf` 和 `third_party/bpftool` 可用（示例的 Makefile 会自动构建 bootstrap bpftool 和静态 libbpf）。
- 推荐：已在顶层构建 bpftime（并启用 CUDA attach）：
  - `cmake -Bbuild -DBPFTIME_ENABLE_CUDA_ATTACH=1 -DBPFTIME_CUDA_ROOT=/usr/local/cuda .`
  - `cmake --build build -j$(nproc)`

## 构建
```bash
cd example/gpu/gpu_shared_map
make
```

这会生成：
- `gpu_shared_map`（host 程序）
- `vec_add`（CUDA 测试 kernel）
- `.output/`（中间产物和 BPF skeleton）

## 运行步骤（Agent/Server 模式）
1) 启动 server（只读进程）：
```bash
/bpftime/build/tools/cli/bpftime load /bpftime/example/gpu/gpu_shared_map/gpu_shared_map
```
2) 启动 agent 的目标程序（加载 CUDA attach，触发 BPF）：
```bash
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
  BPFTIME_LOG_OUTPUT=console SPDLOG_LEVEL=debug example/gpu/gpu_shared_map/vec_add
```
3) 预期输出：
- **Server：** 会周期性打印 `counter[0]=N`，并且它应该单调递增（受并发覆盖影响，但总体趋势向上）。
- **Agent：** 你会看到 `CUDA Received call request id ...` 等相关日志（如果不走 CPU handshake 路径，日志会少很多）。

## 一致性说明（简要）
- **写入：** device 侧执行 `memcpy` 覆盖。写入后会执行系统级 memory fence（在 trampoline 中实现），以确保 host 可见性。
- **读取：** 读取是 lock-free 的。你可能会读到稍旧的值，但不会读到部分写入的值。
- 如果需要“更强的读取一致性”，可以在读取侧加锁或者使用 double-read version check（本示例未启用）。

## 非 per-thread GPU Map 的技术点（当前实现）
- **目标与形式：**
  - **非 per-thread**：GPU 和 host 共享同一份 map（array）；不同线程不再有各自独立的副本。
  - **UVA Zero-Copy**：host 侧共享内存由 agent 注册，使 GPU 和 host 能通过 UVA（Unified Virtual Addressing）看到同一份数据。
- **更新语义：**
  - 直接的 device-side 写入（trampoline fast-path）使用 `memcpy` 覆盖，非原子；最后写入者获胜。写入后的系统 fence 保证可见性。
  - 这种方式不再依赖 CPU handshake，从而降低了延迟和开销。若要精确计数，建议在更高层做聚合，或者通过分片 key 来减少冲突。

## 示例写入方式（更新）
- **BPF 侧**（`gpu_shared_map.bpf.c`）：
  - 在 `kretprobe/vectorAdd` 中，程序读取 `counter[0]`，加 1，然后用 `BPF_ANY` 覆盖写回该值（`memcpy` 在 device 上执行）。

## 故障排查
- **没有 `nvcc`：** 脚本会提示你跳过 CUDA 构建；这个示例就无法触发 counter 增加。
- **权限/依赖：** 确认 clang、make 和 gcc 已安装，并且可以从 `third_party/` 目录构建 libbpf/bpftool。
- **CUDA Driver：** 你必须能够运行一个最小的 CUDA kernel；否则 `vec_add` 会失败。
