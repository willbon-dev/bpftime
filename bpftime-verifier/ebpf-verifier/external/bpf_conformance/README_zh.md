# BPF Conformance
[![CI/CD](https://github.com/Alan-Jowett/bpf_conformance/actions/workflows/CICD.yml/badge.svg?branch=main)](https://github.com/Alan-Jowett/bpf_conformance/actions/workflows/CICD.yml)
[![Coverage Status](https://coveralls.io/repos/github/Alan-Jowett/bpf_conformance/badge.png?branch=main)](https://coveralls.io/github/Alan-Jowett/bpf_conformance?branch=main)

本项目用于衡量 BPF runtime 对 ISA 的符合程度。为了进行符合性测试，会把待测 BPF runtime 构建成一个 plugin 进程，执行以下操作：
1) 接受 BPF byte code 和初始内存。
2) 执行 byte code。
3) 在执行结束时返回 %r0 的值。

## 目前使用本项目进行测量的 eBPF runtime 实现
1) [Linux Kernel via libbpf](https://github.com/Alan-Jowett/bpf_conformance/tree/main/libbpf_plugin)
2) [uBPF](https://github.com/iovisor/ubpf/tree/main/ubpf_plugin)
3) [eBPF for Windows / bpf2c](https://github.com/microsoft/ebpf-for-windows/tree/main/tests/bpf2c_plugin)
4) [rbpf](https://github.com/qmonnet/rbpf/blob/master/examples/rbpf_plugin.rs)
5) [Prevail Verifier](https://github.com/vbpf/ebpf-verifier/blob/main/src/test/test_conformance.cpp)

注意：
Linux Kernel 被视为权威的 eBPF 实现。

## 构建

运行 ```cmake -S . -B build``` 配置项目，然后运行 ```cmake --build build``` 构建项目。

## 使用已发布的包
从 [bpf_conformance](https://github.com/Alan-Jowett/bpf_conformance/pkgs/container/bpf_conformance) 中选择所需版本。

假设包名为："ghcr.io/alan-jowett/bpf_conformance:main"
```
docker run --privileged -it --rm ghcr.io/alan-jowett/bpf_conformance:main src/bpf_conformance_runner --test_file_directory tests --plugin_path libbpf_plugin/libbpf_plugin --cpu_version v3
```

## 运行测试
Linux（测试需要 Linux kernel BPF 支持）：
```
cmake --build build --target test --
```

注意：`libbpf_plugin` 需要 root 权限或 BPF 权限。

## 将 bpf_conformance 作为静态库使用
BPF Conformance 测试也可以作为另一个测试的一部分，以静态库的形式使用。
1) 包含 `include/bpf_conformance.h`
2) 链接 `libbpf_conformance.a` 和 `boost_filesystem`（视平台而定）。
3) 调用 `bpf_conformance`，并传入测试文件列表。

## 结果解读
测试完成后，bpf_conformance 工具会打印通过/失败的测试列表以及汇总计数。

```
sudo build/src/bpf_conformance --test_file_directory tests --plugin_path bui
ld/libbpf_plugin/libbpf_plugin
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
