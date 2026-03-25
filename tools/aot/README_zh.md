# bpftime-aot

基于 LLVM 的 eBPF Ahead-of-Time（AOT）编译器，可将 eBPF bytecode 转换为 native machine code。

## 概览

`bpftime-aot` 是一个命令行工具，可以把 eBPF 程序编译为 native ELF 对象，以便在用户态高性能执行。它支持：

- 从 eBPF bytecode 进行 AOT 编译，生成 native x86/ARM machine code
- 多种输入来源：eBPF ELF 文件或共享内存中的程序
- 已编译程序的独立执行
- helper function relocation，便于无缝集成
- 导出 LLVM IR，便于调试和优化分析

底层库请参见 [llvmbpf](https://github.com/eunomia-bpf/llvmbpf)。

## 安装

在构建 bpftime 之后，工具位于：
```bash
~/.bpftime/bpftime-aot
# 或加入 PATH
export PATH=$PATH:~/.bpftime/
```

## 用法

```console
bpftime-aot [--help] [--version] {build,compile,load,run}

子命令：
  build      从 eBPF ELF 对象文件构建 native ELF
  compile    编译加载到 bpftime 共享内存中的 eBPF 程序
  load       将已编译的 native ELF 加载到共享内存
  run        执行已编译的 native ELF 程序
```

## 命令参考

### build - 从 eBPF ELF 编译

把 eBPF ELF 对象文件中的程序编译为 native code：

```bash
bpftime-aot build <EBPF_ELF> [-o OUTPUT_DIR] [-e]
```

### compile - 从共享内存编译

编译已经加载到 bpftime 共享内存中的 eBPF 程序：

```bash
bpftime-aot compile [-o OUTPUT_DIR] [-e]
```

### load - 把编译后的 ELF 加载到共享内存

```bash
bpftime-aot load <PATH> <ID>
```

### run - 执行编译后的程序

```bash
bpftime-aot run <PATH> [MEMORY]
```

## 集成示例

### 与自定义程序链接

你可以把编译后的 eBPF 程序与你的 C/C++ 应用链接在一起。

### Helper 函数命名约定

### 理解 relocation

## 高级用法

### 导出 LLVM IR

### 示例输出

## 性能收益

AOT 编译带来明显的性能优势：
- 没有 JIT 开销
- 生成经过优化的 native code
- 启动更快
- 指令缓存利用率更好

典型加速比：比 JIT 快 2-5 倍，比解释器快 10-50 倍。

## 故障排查

- `"Unable to open BPF elf"`：请确认 eBPF ELF 由 clang 编译，并包含有效的 BTF 信息。
- `"Invalid id not exist"`：使用 `bpftimetool export` 检查程序 ID 是否存在于共享内存中。
- Helper 函数未定义：在 driver 程序中实现所有需要的 `_bpf_helper_ext_XXXX` 函数。

## 另见

- [bpftimetool](https://github.com/eunomia-bpf/bpftime/tree/master/tools/bpftimetool)
- [optimize.md](https://github.com/eunomia-bpf/bpftime/blob/master/tools/aot/optimize.md)
- [llvmbpf](https://github.com/eunomia-bpf/llvmbpf)
- [bpftime 文档](https://github.com/eunomia-bpf/bpftime)
