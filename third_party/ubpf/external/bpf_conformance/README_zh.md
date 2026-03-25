# BPF Conformance
[![CI/CD](https://github.com/Alan-Jowett/bpf_conformance/actions/workflows/CICD.yml/badge.svg?branch=main)](https://github.com/Alan-Jowett/bpf_conformance/actions/workflows/CICD.yml)
[![Coverage Status](https://coveralls.io/repos/github/Alan-Jowett/bpf_conformance/badge.png?branch=main)](https://coveralls.io/github/Alan-Jowett/bpf_conformance?branch=main)

这个项目用于衡量一个 BPF runtime 对 ISA 的符合程度。为了进行符合性测试，会把被测的 BPF runtime 构建成一个插件进程，该进程需要：
1) 接受 BPF byte code 和初始内存。
2) 执行 byte code。
3) 在执行结束时返回 `%r0` 的值。

## 目前使用这个项目进行测量的 eBPF runtime 实现
1) [Linux Kernel via libbpf](https://github.com/Alan-Jowett/bpf_conformance/tree/main/libbpf_plugin)
2) [uBPF](https://github.com/iovisor/ubpf/tree/main/ubpf_plugin)
3) [eBPF for Windows / bpf2c](https://github.com/microsoft/ebpf-for-windows/tree/main/tests/bpf2c_plugin)
4) [rbpf](https://github.com/qmonnet/rbpf/blob/master/examples/rbpf_plugin.rs)
5) [Prevail Verifier](https://github.com/vbpf/ebpf-verifier/blob/main/src/test/test_conformance.cpp)

注意：
Linux Kernel 被视为权威的 eBPF 实现。

## 前置条件

### Ubuntu

```
sudo apt-get install -y libboost-dev libboost-filesystem-dev libboost-program-options-dev libelf-dev lcov libbpf-dev
```

### MacOS

```
brew install cmake ninja ccache boost
```

## 构建

运行 ```cmake -S . -B build``` 来配置项目，然后运行 ```cmake --build build``` 来构建项目。

## 用法

```
Options:
  --help                         Print help messages
  --test_file_path arg           Path to test file
  --test_file_directory arg      Path to test file directory
  --plugin_path arg              Path to plugin
  --plugin_options arg           Options to pass to plugin
  --list_instructions arg        List instructions used and not used in tests
  --list_used_instructions arg   List instructions used in tests
  --list_unused_instructions arg List instructions not used in tests
  --debug (true|false)           Print debug information
  --xdp_prolog (true|false)      XDP prolog
  --elf (true|false)             ELF format
  --cpu_version arg              CPU version
  --include_regex arg            Include regex
  --exclude_regex arg            Exclude regex
```

`--xdp_prolog true` 只能和 `libbpf_plugin` 一起使用。

## 使用已发布的软件包
从 [bpf_conformance](https://github.com/Alan-Jowett/bpf_conformance/pkgs/container/bpf_conformance) 中选择你需要的版本。

假设包名为 `"ghcr.io/alan-jowett/bpf_conformance:main"`：
```
docker run --privileged -it --rm ghcr.io/alan-jowett/bpf_conformance:main src/bpf_conformance_runner --test_file_directory tests --plugin_path libbpf_plugin/libbpf_plugin --cpu_version v3
```

## 运行测试
Linux（测试需要 Linux kernel BPF 支持）：
```
cmake --build build --target test --
```

注意：`libbpf_plugin` 需要 root 或 BPF 权限。

## 将 bpf_conformance 作为静态库使用
BPF Conformance 测试也可以作为静态库，用于其他测试的一部分。
1) 包含 include/bpf_conformance.h
2) 链接 libbpf_conformance.a 和 boost_filesystem（具体取决于平台）。
3) 调用 bpf_conformance，并传入测试文件列表。

## 结果解读
测试完成后，bpf_conformance 工具会打印通过/失败的测试列表以及汇总数量。

```
sudo build/src/bpf_conformance --test_file_directory tests --plugin_path build/libbpf_plugin/libbpf_plugin
Test results:
PASS: "tests/add.data"
PASS: "tests/add64.data"
PASS: "tests/alu-arith.data"
PASS: "tests/alu-bit.data"
PASS: "tests/alu64-arith.data"
PASS: "tests/alu64-bit.data"
PASS: "tests/arsh-reg.data"
PASS: "tests/arsh.data"
PASS: "tests/arsh32-high-shift.data"
PASS: "tests/arsh64.data"
PASS: "tests/be16-high.data"
PASS: "tests/be16.data"
PASS: "tests/be32-high.data"
PASS: "tests/be32.data"
PASS: "tests/be64.data"
PASS: "tests/call_unwind_fail.data"
PASS: "tests/div-by-zero-reg.data"
PASS: "tests/div32-high-divisor.data"
PASS: "tests/div32-imm.data"
PASS: "tests/div32-reg.data"
PASS: "tests/div64-by-zero-reg.data"
PASS: "tests/div64-imm.data"
PASS: "tests/div64-reg.data"
PASS: "tests/exit-not-last.data"
PASS: "tests/exit.data"
PASS: "tests/jeq-imm.data"
PASS: "tests/jeq-reg.data"
PASS: "tests/jge-imm.data"
PASS: "tests/jgt-imm.data"
PASS: "tests/jgt-reg.data"
PASS: "tests/jit-bounce.data"
PASS: "tests/jle-imm.data"
PASS: "tests/jle-reg.data"
PASS: "tests/jlt-imm.data"
PASS: "tests/jlt-reg.data"
PASS: "tests/jne-reg.data"
PASS: "tests/jset-imm.data"
PASS: "tests/jset-reg.data"
PASS: "tests/jsge-imm.data"
PASS: "tests/jsge-reg.data"
PASS: "tests/jsgt-imm.data"
PASS: "tests/jsgt-reg.data"
PASS: "tests/jsle-imm.data"
PASS: "tests/jsle-reg.data"
PASS: "tests/jslt-imm.data"
PASS: "tests/jslt-reg.data"
PASS: "tests/lddw.data"
PASS: "tests/lddw2.data"
PASS: "tests/ldxb-all.data"
PASS: "tests/ldxb.data"
PASS: "tests/ldxdw.data"
PASS: "tests/ldxh-all.data"
PASS: "tests/ldxh-all2.data"
PASS: "tests/ldxh-same-reg.data"
PASS: "tests/ldxh.data"
PASS: "tests/ldxw-all.data"
PASS: "tests/ldxw.data"
PASS: "tests/le16.data"
PASS: "tests/le32.data"
PASS: "tests/le64.data"
PASS: "tests/lsh-reg.data"
PASS: "tests/mem-len.data"
PASS: "tests/mod-by-zero-reg.data"
PASS: "tests/mod.data"
PASS: "tests/mod32.data"
PASS: "tests/mod64-by-zero-reg.data"
PASS: "tests/mod64.data"
PASS: "tests/mov.data"
PASS: "tests/mul32-imm.data"
PASS: "tests/mul32-reg-overflow.data"
PASS: "tests/mul32-reg.data"
PASS: "tests/mul64-imm.data"
PASS: "tests/mul64-reg.data"
PASS: "tests/neg.data"
PASS: "tests/neg64.data"
PASS: "tests/prime.data"
PASS: "tests/rsh-reg.data"
PASS: "tests/rsh32.data"
PASS: "tests/stack.data"
PASS: "tests/stb.data"
PASS: "tests/stdw.data"
PASS: "tests/sth.data"
PASS: "tests/stw.data"
PASS: "tests/stxb-all.data"
PASS: "tests/stxb-all2.data"
PASS: "tests/stxb-chain.data"
PASS: "tests/stxb.data"
PASS: "tests/stxdw.data"
PASS: "tests/stxh.data"
PASS: "tests/stxw.data"
PASS: "tests/subnet.data"
Passed 91 out of 91 tests.
```

## bpf_conformance_runner 插件

bpf_conformance_runner 通过命令行执行插件，并使用 stdin、stdout 和 stderr 交换额外信息，格式如下：

```
<plugin name> [<base16 memory bytes>] [<plugin options>] [--elf]
```

其中：
* `<plugin name>`：插件可执行文件名
* `<base16 memory bytes>`：如果存在，则表示测试数据文件中 `mem` section 的内容
* `<plugin options>`：传给插件的额外参数
* `--elf`：如果存在，则表示传给 stdin 的数据将使用 ELF 格式

随后程序会通过 stdin 传给插件，要么是原始 bytecode，要么（如果指定了 `--elf`）是 ELF 格式。
插件必须满足以下任一条件：
* 计算成功结果，并将 `r0` 的最终内容以十六进制输出到 stdout（可以带或不带 `0x` 前缀），然后以状态码 0 退出，或者
* 输出错误信息到 stderr，并以非 0 状态码退出。

基于上述规范可以创建更多插件。
