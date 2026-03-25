### eBPF Direct-run vs Native CUDA（最新）

**设备**：Tesla P40  
**时间戳**：2025-10-21

#### VecAdd（最小预设）

| Test | Avg Time (μs) | Baseline | Overhead |
|---|---:|---:|---:|
| Baseline (minimal, CUDA kernel) | 16.78 | - | - |
| eBPF Direct Run VecAdd (minimal) | 27.58 | 16.78 | 1.64x (+64.4%) |

注：基于最新的 `benchmark/gpu/micro/examples_vec_add_result.md`（README 中的手动运行路径）。

#### GEMM（最小预设）

| Test | Avg Time (μs) | Baseline | Overhead |
|---|---:|---:|---:|
| Baseline (minimal, CUDA kernel) | 2255.38 | - | - |
| eBPF Direct Run GEMM (minimal) | 2336.83 | 2255.38 | 1.04x (+3.6%) |

注：数据来自 `benchmark/gpu/micro/micro_gemm_result.md` 的最小案例（32×32×32，grid=2×2，block=16×16；direct-run 脚本：`benchmark/gpu/micro/run_direct_gemm.sh`）。
