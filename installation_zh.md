# 安装与测试

## 目录

<!-- TOC -->

- [构建与测试](#building-and-test)
  - [目录](#table-of-contents)
  - [使用 docker 镜像](#use-docker-image)
  - [安装依赖](#install-dependencies)
    - [构建并安装所有内容](#build-and-install-all-things)
  - [关于构建的详细说明](#detailed-things-about-building)
    - [构建选项](#build-options)
    - [以 release 模式构建并安装完整 runtime（使用 ubpf jit）](#build-and-install-the-complete-runtime-in-release-modewith-ubpf-jit)
    - [以 debug 模式构建并安装完整 runtime（使用 ubpf jit）](#build-and-install-the-complete-runtime-in-debug-modewith-ubpf-jit)
    - [以 release 模式构建并安装完整 runtime（使用 llvm jit）](#build-and-install-the-complete-runtime-in-release-modewith-llvm-jit)
    - [启用 LTO 编译](#compile-with-lto-enabled)
    - [使用 userspace verifier 编译](#compile-with-userspace-verifier)
    - [禁用 libbpf 编译](#compile-with-libbpf-disabled)
    - [测试目标](#testing-targets)
  - [只编译 vm（不含 runtime，不含 uprobe）](#compile-only-the-vm-no-runtime-no-uprobe)
  - [更多编译选项](#more-compile-options)

<!-- /TOC -->

## 使用 docker 镜像

我们提供了用于构建和测试 bpftime 的 docker 镜像。

```bash
# 运行容器
docker run -it --rm --name test_bpftime -v "$(pwd)":/workdir -w /workdir ghcr.io/eunomia-bpf/bpftime:latest /bin/bash
# 在容器中打开另一个 shell（如有需要）
docker exec -it test_bpftime /bin/bash
```

或者也可以直接通过 dockerfile 构建镜像：

```bash
git submodule update --init --recursive
docker build .
```

## 安装依赖

安装所需软件包：

```bash
sudo apt-get update && sudo apt-get install \
        libelf1 libelf-dev zlib1g-dev make cmake git libboost-all-dev \
        binutils-dev libyaml-cpp-dev ca-certificates clang llvm pkg-config llvm-dev
git submodule update --init --recursive
```

我们已经在 Ubuntu 23.04 上测试过。推荐 `gcc` >= 12.0.0，`clang` >= 16.0.0。建议使用 `libboost1.74-all-dev`。

在 Ubuntu 20.04 上，你可能需要手动切换到 gcc-12。

### 构建并安装所有内容

把所有可以安装到 `~/.bpftime` 的内容都安装进去，包括：

- `bpftime`：用于把 agent 和 server 注入到用户态程序的 cli 工具
- `bpftime-vm`：用于将 eBPF 程序编译为 native 程序，或者运行已编译程序的 cli 工具
- `bpftimetool`：用于管理存放在共享内存中的内容，例如 maps 或 programs 的数据
- `bpftime_daemon`：用于实现类似 syscall server 的功能，但不需要注入到用户态程序中的可执行文件
- `libbpftime-agent.so`、`libbpftime-agent-transformer.so`：bpftime agent 所需的库
- `libbpftime-syscall-server.so`：bpftime syscall server 所需的库

使用 makefile 构建：

```bash
make release JOBS=$(nproc) # 构建并安装 runtime
export PATH=$PATH:~/.bpftime
```

也可以使用 `cmake` 构建（Makefile 只是 cmake 命令的一个包装）：

```bash
cmake -Bbuild  -DCMAKE_BUILD_TYPE:STRING=Release \
           -DSPDLOG_ACTIVE_LEVEL=SPDLOG_LEVEL_INFO
cmake --build build --config Release --target install
export PATH=$PATH:~/.bpftime
```

然后就可以运行 cli：

```console
$ bpftime
Usage: bpftime [OPTIONS] <COMMAND>
...
```

更多常用命令请参见 [Makefile](https://github.com/eunomia-bpf/bpftime/blob/master/Makefile)。

## 关于构建的详细说明

我们使用 cmake 作为构建系统。

### 构建选项

你可能会对下面这些 cmake 选项感兴趣：

- `CMAKE_BUILD_TYPE`：指定构建类型，可为 `Debug`、`Release`、`MinSizeRel` 或 `RelWithDebInfo`。如果你不打算调试 bpftime，只需要设置为 `Release`。默认值为 `Debug`。
- `BPFTIME_ENABLE_UNIT_TESTING`：是否构建单元测试目标。详情请参见 `Testing targets`。默认值为 `NO`。
- `BPFTIME_ENABLE_LTO`：是否启用 Link Time Optimization。启用后可能增加编译时间，但可能带来更好的性能。默认值为 `No`。
- `BPFTIME_ENABLE_CCACHE`：是否启用 Ccache 以加快重建速度。默认值为 `OFF`。
- `BPFTIME_ENABLE_ASAN`：是否启用 Address Sanitizer 以检测内存错误。默认值为 `OFF`。
- `ENABLE_EBPF_VERIFIER`：是否启用 userspace eBPF verifier。默认值为 `OFF`。
- `BPFTIME_LLVM_JIT`：是否使用 LLVM JIT 作为 eBPF runtime。需要 LLVM >= 15。推荐启用，因为 ubpf interpreter 已不再维护。默认值为 `ON`。
- `BPFTIME_UBPF_JIT`：是否使用 uBPF JIT backend。默认值为 `ON`。
- `LLVM_DIR`：指定 LLVM 的安装目录。CMake 可能无法自动发现 LLVM 安装。请把此选项设置为包含 `LLVMConfig.cmake` 的目录，例如 Ubuntu 上的 `/usr/lib/llvm-15/cmake`。
- `BUILD_BPFTIME_DAEMON`：构建 daemon，用于把 eBPF 程序加载到内核中并使用 kernel verifier。默认值为 `ON`。
- `BPFTIME_BUILD_WITH_LIBBPF`：是否在构建 bpftime 时包含 libbpf。关闭后只能在用户态运行，但可以更容易移植到其他平台，例如 macOS。默认值为 `ON`。
- `BPFTIME_BUILD_KERNEL_BPF`：是否构建带有 bpf share maps 的版本。默认值为 `ON`。
- `BPFTIME_BUILD_STATIC_LIB`：是否把 bpftime runtime 构建为完整的静态库，方便链接到其他程序。默认值为 `OFF`。
- `BPFTIME_ENABLE_MPK`：是否为共享内存启用 Memory Protection Keys。默认值为 `OFF`。
- `BPFTIME_ENABLE_IOURING_EXT`：是否启用 iouring helpers 扩展。默认值为 `OFF`。
- `ENABLE_PROBE_WRITE_CHECK`：是否启用 probe write 检查。它会检查 `bpf_probe_write_user` 操作，并在 probe write 地址非法时报告错误。默认值为 `ON`。
- `ENABLE_PROBE_READ_CHECK`：是否启用 probe read 检查。它会检查 `bpf_probe_write` 操作，并在 probe read 地址非法时报告错误。默认值为 `ON`。
- `BPFTIME_ENABLE_CUDA_ATTACH`：是否启用 CUDA/GPU attach 支持。需要把 `BPFTIME_CUDA_ROOT` 设置为 CUDA 安装目录，例如 `/usr/local/cuda-12.8`。默认值为 `OFF`。
- `BPFTIME_CUDA_ROOT`：指定 CUDA 安装根目录。只有在 `BPFTIME_ENABLE_CUDA_ATTACH=1` 时才需要。
- `BPFTIME_WARNINGS_AS_ERRORS`：是否把编译警告视为错误。默认值为 `OFF`。
- `BPFTIME_VERBOSE_OUTPUT`：是否启用详细输出，以便更好地理解每一步操作。默认值为 `ON`。

所有构建选项请参见 <https://github.com/eunomia-bpf/bpftime/blob/master/cmake/StandardSettings.cmake>。

### 以 release 模式构建并安装完整 runtime（使用 ubpf jit）

```bash
cmake -Bbuild -DCMAKE_BUILD_TYPE=Release -DBPFTIME_ENABLE_LTO=NO
cmake --build build --config Release --target install
```

### 以 debug 模式构建并安装完整 runtime（使用 ubpf jit）

```bash
cmake -Bbuild -DCMAKE_BUILD_TYPE=Debug -DBPFTIME_ENABLE_LTO=NO
cmake --build build --config Debug --target install
```

### 以 release 模式构建并安装完整 runtime（使用 llvm jit）

```bash
cmake -Bbuild -DCMAKE_BUILD_TYPE=Release -DBPFTIME_ENABLE_LTO=NO -DBPFTIME_LLVM_JIT=YES
cmake --build build --config RelWithDebInfo --target install
```

### 启用 LTO 编译

只需把 `BPFTIME_ENABLE_LTO` 设置为 `YES`。

例如，构建包含 llvm-jit 和 LTO 的包：

```sh
cmake -Bbuild -DCMAKE_BUILD_TYPE=Release -DBPFTIME_ENABLE_LTO=YES -DBPFTIME_LLVM_JIT=YES
cmake --build build --config RelWithDebInfo --target install
```

### 使用 userspace verifier 编译

注意，我们使用 <https://github.com/vbpf/ebpf-verifier> 作为 userspace verifier。它并不完美，可能不支持某些特性（例如 ringbuf）。

```sh
cmake -DBPFTIME_LLVM_JIT=NO -DENABLE_EBPF_VERIFIER=YES -DCMAKE_BUILD_TYPE=Release -B build
cmake --build build --config Release --target install
```

### 禁用 libbpf 编译

这个标志可用于在 macOS 上编译 `bpftime`。它会禁用 bpftime 中所有与 libbpf 相关的库和特性。

```sh
cmake -Bbuild -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo -DBPFTIME_BUILD_WITH_LIBBPF=OFF -DBPFTIME_BUILD_KERNEL_BPF=OFF
cmake --build build --config RelWithDebInfo  --target install -j$(JOBS)
```

### 编译 CUDA/GPU attach 支持

要启用 CUDA attach 支持，请设置 `BPFTIME_ENABLE_CUDA_ATTACH=1` 并指定 CUDA 安装路径：

```sh
# 以 CUDA 12.8 为例
cmake -Bbuild -DCMAKE_BUILD_TYPE=Release -DBPFTIME_ENABLE_CUDA_ATTACH=1 -DBPFTIME_CUDA_ROOT=/usr/local/cuda-12.8
cmake --build build --config Release --target install
```

注意：请确保 `BPFTIME_CUDA_ROOT` 指向你的 CUDA 安装目录（例如 `/usr/local/cuda-12.8`、`/usr/local/cuda-12.6` 等）。

### 测试目标

我们提供了一些单元测试目标，它们是：

- `bpftime_daemon_tests`
- `bpftime_runtime_tests`
- `llvm_jit_tests`

只有在把 `BPFTIME_ENABLE_UNIT_TESTING` 设置为 `YES` 时，这些目标才会启用。

构建并运行它们进行测试，例如：

```sh
cmake -DCMAKE_PREFIX_PATH=/usr/include/llvm -DBPFTIME_LLVM_JIT=YES -DBPFTIME_ENABLE_UNIT_TESTING=YES -DCMAKE_BUILD_TYPE=Release -B build
cmake --build build --config RelWithDebInfo --target bpftime_runtime_tests
sudo ./build/runtime/unit-test/bpftime_runtime_tests
```

## 只编译 vm（不含 runtime，不含 uprobe）

如果你想要一个不包含 runtime 的轻量级构建（只保留 vm library 和 LLVM JIT）：

```bash
make build-vm # 构建带简单 jit 的简单 vm
make build-llvm # 构建带 llvm jit 的 vm
```

## 更多编译选项

所有 cmake 构建选项请参见 <https://github.com/eunomia-bpf/bpftime/blob/master/cmake/StandardSettings.cmake>。
