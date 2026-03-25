# directly_run

一个直接在 GPU 上运行 eBPF 程序的简单示例。

````
make -j8
bpftime load ./directly_run &
bpftimetool run-on-cuda cuda__run
````

VecAdd（direct-run）快速开始：

````
make -j8
build/tools/cli/bpftime load ./directly_run &
# 可选：为 N=1024 指定 grid/block（4 个 block x 256 个线程）
build/tools/bpftimetool/bpftimetool run-on-cuda cuda__vec_add 1 4 1 1 256 1 1
````

GEMM（direct-run）快速开始：

````
make -j8
build/tools/cli/bpftime load ./directly_run &
# 示例：64x64，grid=4x4，block=16x16
build/tools/bpftimetool/bpftimetool run-on-cuda cuda__gemm 1 4 4 1 16 16 1
````

基线与 eBPF 对比（手动）：

````
# 基线（原生 CUDA vec_add），例如最小预设
benchmark/gpu/workload/vec_add 10000 10000 256 40

# eBPF direct-run vec_add（不需要 workload 二进制）
build/tools/cli/bpftime load ./directly_run &
build/tools/bpftimetool/bpftimetool run-on-cuda cuda__vec_add 1 4 1 1 256 1 1

# 基线（原生 CUDA GEMM），例如最小预设
benchmark/gpu/workload/matrixMul 32 3 32 1

# eBPF direct-run GEMM（不需要 workload 二进制）
build/tools/cli/bpftime load ./directly_run &
build/tools/bpftimetool/bpftimetool run-on-cuda cuda__gemm 1 4 4 1 16 16 1
````

基准测试快速运行（输出 md/json/log）：

````
# VecAdd 基准（包含 baseline 与 direct-run 对比）
python3 benchmark/gpu/run_cuda_bench.py benchmark/gpu/micro/examples_vec_add_config.json
# 结果：benchmark/gpu/micro/examples_vec_add_result.md/json/log

# GEMM 基准（baseline 加上 micro 测试）
python3 benchmark/gpu/run_cuda_bench.py benchmark/gpu/micro/micro_gemm_config.json
# 结果：benchmark/gpu/micro/micro_gemm_result.md/json/log
````
