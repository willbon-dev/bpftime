[![Coverage Status](https://coveralls.io/repos/github/vbpf/ebpf-verifier/badge.svg?branch=main)](https://coveralls.io/github/vbpf/ebpf-verifier?branch=main)[![CodeQL](https://github.com/vbpf/ebpf-verifier/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/vbpf/ebpf-verifier/actions/workflows/codeql-analysis.yml)

# PREVAIL
## 一款基于抽象解释层的多项式时间运行 EBPF verifier

一个新的 eBPF verifier。

[PLDI 论文](https://vbpf.github.io/assets/prevail-paper.pdf) 中讨论的版本可在 [这里](https://github.com/vbpf/ebpf-verifier/tree/d29fd26345c3126bf166cf1c45233a9b2f9fb0a0) 获取。

## 入门

### Ubuntu 原生依赖
```bash
sudo apt install build-essential git cmake libboost-dev libyaml-cpp-dev
sudo apt install libboost-filesystem-dev libboost-program-options-dev
```

### Windows 原生依赖

* 安装 [git](https://git-scm.com/download/win)
* 安装 [Visual Studio Build Tools 2022](https://aka.ms/vs/17/release/vs_buildtools.exe)，并选择 "C++ build tools" 工作负载（Visual Studio Build Tools 2022 支持 CMake 3.25）
* 安装 [nuget.exe](https://www.nuget.org/downloads)

### 安装
克隆：
```
git clone --recurse-submodules https://github.com/vbpf/ebpf-verifier.git
cd ebpf-verifier
```

Ubuntu 上构建：
```
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

Windows 上构建（使用多配置生成器）：
```
cmake -B build
cmake --build build --config Release
```

### 使用 Docker 运行
构建并运行：
```bash
docker build -t verifier .
docker run -it verifier ebpf-samples/cilium/bpf_lxc.o 2/1
1,0.009812,4132
# 要运行 Linux verifier，你需要一个具备特权的容器：
docker run --privileged -it verifier ebpf-samples/linux/cpustat_kern.o --domain=linux
```

### 示例：
```
ebpf-verifier$ ./check ebpf-samples/cilium/bpf_lxc.o 2/1
1,0.008288,4064
```
输出是三个以逗号分隔的值：
* 1 或 0，分别表示“通过”和“失败”
* fixpoint 算法的运行时间（秒）
* 峰值内存占用（kb），以 resident-set size（rss）表示

## 用法：
```
A new eBPF verifier
Usage: ./check [OPTIONS] path [section]

Positionals:
  path FILE REQUIRED          待分析的 Elf 文件
  section SECTION             待分析的 section

Options:
  -h,--help                   打印此帮助并退出
  -l                          列出 sections
  -d,--dom,--domain DOMAIN:{cfg,linux,stats,zoneCrab}
                              抽象域
  --termination               验证终止性
  --assume-assert             假定断言成立
  -i                          打印不变式
  -f                          打印 verifier 的失败日志
  -s                          应用会导致运行时失败的额外检查
  -v                          同时打印不变式和失败信息
  --no-division-by-zero       不允许除零
  --no-simplify               不进行简化
  --line-info                 打印行号信息
  --asm FILE                  将反汇编输出到 FILE
  --dot FILE                  将控制流图导出到 dot FILE

你可以使用 @headers 作为 path，这样只会显示输出字段的表头。
```

`--asm` 标志的标准替代方案是 `llvm-objdump -S FILE`。

可以使用 `dot` 和常规 PDF 查看器查看 cfg：
```
sudo apt install graphviz
./check ebpf-samples/cilium/bpf_lxc.o 2/1 --dot cfg.dot
dot -Tpdf cfg.dot > cfg.pdf
```

## 测试 Linux verifier

要运行 Linux verifier，必须使用 `sudo`：
```
sudo ./check ebpf-samples/linux/cpustat_kern.o tracepoint/power/cpu_idle --domain=linux
```
