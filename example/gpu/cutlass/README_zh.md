# CUTLASS GPU Demo

这个目录包含一个完整的 GPU attach demo，它把一个较重的 CUTLASS GEMM 负载和一个对应的 eBPF launch counter 组合在一起。通过调整矩阵形状和 launch 次数，你可以从快速 smoke test 一直扩展到接近生产级 GEMM/BatchGEMM 负载的 kernel（类似 LLM 场景中的 4K–8K 问题）。

- `gemm/`：C++ driver，用来实例化 `cutlass::gemm::device::Gemm<float,...>`，并允许你配置矩阵大小、warmup 次数、launch 次数、随机种子以及可选的 CPU 验证。
- `counter/`：eBPF kretprobe（`cutlass_launch_counter`），挂载到 CUTLASS kernel，并在 kernel 每次退出时递增 GPU array map。

下面的内容已经取代了子目录里的 README，因此你只需要看这个文件就够了。

## 构建

```bash
# 从仓库根目录开始
make -C example/gpu/cutlass CUTLASS_DIR=.../cutlass
```

- `CUTLASS_DIR` 是可选的；如果不提供，Makefile 会把 CUTLASS v3.5.0 克隆到 `.deps/cutlass`。
- 构建 bpftime 本身时请启用 CUDA attach（`-DBPFTIME_ENABLE_CUDA_ATTACH=ON`），这样 syscall-server / agent shim 才会存在。

## 负载选项（`gemm/cutlass_gemm`）

```
cutlass_gemm [--shape MxNxK] [--m M] [--n N] [--k K]
             [--launches N] [--warmup N] [--seed S] [--verify]
```

- `--shape` 是 M/N/K 的简写（默认 `4096x4096x4096`）。
- `--launches` 控制 warmup 之后的计时 kernel launch 次数（默认 `24`）。
- `--warmup` 在计时前额外运行若干次 launch（默认 `2`）。
- `--verify` 为矩阵 ≤512³ 启用 CPU 参考检查；更大的 shape 会自动跳过检查。
- `--seed` 用于可复现地设置 host 端 RNG（默认 `42`）。

运行结束后，二进制会打印总时间/平均时间、近似 GFLOP/s 速率，以及结果 tensor 的 checksum 和 L2 norm，方便你在调参时区分不同运行。

## 运行 Demo

在两个终端中分别运行 counter（server）和 workload：

1. **终端 A - 在 syscall-server shim 下运行 counter**

```bash
BPFTIME_LOG_OUTPUT=console \
LD_PRELOAD=build/runtime/syscall-server/libbpftime-syscall-server.so \
   example/gpu/cutlass/counter/cutlass_launch_counter
```

   counter 会打印带累计 launch 次数的时间戳（例如 `12:34:56 CUTLASS launches: 84`）。

2. **终端 B - 在 agent shim 下运行 CUTLASS workload**

```bash
BPFTIME_LOG_OUTPUT=console \
LD_PRELOAD=build/runtime/agent/libbpftime-agent.so \
   example/gpu/cutlass/gemm/cutlass_gemm --shape 4096x4096x4096 --launches 24 --warmup 2
```

如果只是快速验证，可以切换成更轻的配置，例如 `--shape 1024x1024x1024 --launches 4 --verify`。

只要 workload 开始运行，终端 A 的 counter 就会通过 GPU array map 反映每次 kernel exit，证明 bpftime 的 CUDA attach 路径可以处理大型、手工构造的 PTX。

### 示例输出

终端 A（server）：

```
12:34:56 CUTLASS launches: 24
12:34:57 CUTLASS launches: 48
12:34:58 CUTLASS launches: 72
```

终端 B（workload），默认重负载场景：

```
[cutlass] problem: 4096x4096x4096 | launches=24 (warmup=2) | host seed=42
[cutlass] running 2 warmup launches...
[cutlass] running timed workload...
[cutlass] completed 24 launches in 551.21 ms (avg 22.97 ms) | 5984.17 GFLOP/s
[cutlass] checksum=4631.49 | l2-norm=87387.3
```

不同 GPU 的数值会略有差异，但你应该始终能看到 counter 随着 workload 的 launch 数同步增长，并且 GEMM 二进制会打印 timing/GFLOP/s 摘要。

## 自定义目标 kernel

`counter/cutlass_launch_counter.bpf.c` 中使用了默认 `cutlass_gemm` 模板实例化生成的 kernel 名字。如果你修改了模板参数（tile shape、op class、accumulation type 等），就需要更新 `SEC` 注解：

1. 重新构建 workload（`make -C example/gpu/cutlass/gemm CUTLASS_DIR=.../cutlass`）。
2. 提取 mangled 后的 kernel 符号：

   ```bash
   cuobjdump --dump-elf-symbols example/gpu/cutlass/gemm/cutlass_gemm | grep Gemm
   ```

3. 把 `counter/cutlass_launch_counter.bpf.c` 里的 `SEC` 字符串替换成新名字，然后通过 `make -C example/gpu/cutlass counter` 重新构建 counter。

就是这样，这个 README 现在同时覆盖了负载和 counter 两部分，因此你可以删掉本地旧的分目录说明。
