# bpftime-vm cli 工具

```console
# bpftime-vm
Usage: bpftime-vm [--help] [--version] {build,run}

Optional arguments:
  -h, --help     显示帮助信息并退出
  -v, --version  打印版本信息并退出

Subcommands:
  build         从 eBPF ELF 构建 native ELF；eBPF ELF 中的每个程序都会被编译成单独的 native ELF
  run           运行一个 native eBPF 程序
```

这是 llvm-jit 的 AOT CLI 编译器。

它可以把 ebpf ELF 构建成 native elf，也可以执行编译后的 native elf。**不支持 helpers 和 relocations。对于 helpers 和 maps，请使用 [bpftime/tools](https://github.com/eunomia-bpf/bpftime) 中的 bpftime aot cli。**
