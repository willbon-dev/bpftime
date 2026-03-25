# PTX 代码的 trampoline

- `default_trampoline.cu` 是一个模板程序，内置的 map 操作 trampoline 就来自这里。
- `default_trampoline-cuda-nvptx64-nvidia-cuda-sm_60.s` 是由 `test.cu` 生成的 PTX 代码，通过执行 `clang++-17 -S ./default_trampoline.cu -Wall --cuda-gpu-arch=sm_60 -O2 -L/usr/local/cuda/lib64/ -lcudart` 得到。这里去掉 `bpf_main` 后的 PTX 代码会放入 `../trampoline_ptx.h`。
