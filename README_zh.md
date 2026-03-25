# bpftime：面向可观测性、网络、GPU 及通用扩展框架的用户态 eBPF runtime

[![Build and Test VM](https://github.com/eunomia-bpf/bpftime/actions/workflows/test-vm.yml/badge.svg)](https://github.com/eunomia-bpf/bpftime/actions/workflows/test-vm.yml)
[![Build and test runtime](https://github.com/eunomia-bpf/bpftime/actions/workflows/test-runtime.yml/badge.svg)](https://github.com/eunomia-bpf/bpftime/actions/workflows/test-runtime.yml)
[![DOI](https://zenodo.org/badge/676866666.svg)](https://doi.org/10.48550/arXiv.2311.07923)

`bpftime` 是一个面向用户态的高性能 eBPF runtime 和通用扩展框架。它通过绕过内核并使用诸如 `LLVM` 之类的优化编译器，让 `Uprobe`、`USDT`、`Syscall hooks`、`XDP` 等事件源拥有更高的执行效率。

📦 [主要特性](#key-features) \
🔨 [快速开始](#quick-start-uprobe) \
🔌 [示例与使用场景](#examples--use-cases) \
⌨️ [Linux Plumbers 23 演讲](https://lpc.events/event/17/contributions/1639/) \
📖 [幻灯片](https://eunomia.dev/bpftime/documents/userspace-ebpf-bpftime-lpc.pdf) \
📚 [OSDI '25 论文](https://www.usenix.org/conference/osdi25/presentation/zheng-yusheng)

[**查看 eunomia.dev 上的文档**](https://eunomia.dev/bpftime/) 以及 [Deepwiki](https://deepwiki.com/eunomia-bpf/bpftime)！

bpftime 不是 `userspace eBPF VM`，它是一个用户态 runtime 框架，包含在用户态运行 eBPF 所需的一切：`loader`、`verifier`、`helpers`、`maps`、`ufunc`，以及可观测性、网络、策略或访问控制等多种 `events`。它支持多种 VM 后端选项。若你只需要 eBPF VM，请查看 [llvmbpf](https://github.com/eunomia-bpf/llvmbpf)。

> ⚠️ **注意**：`bpftime` 目前仍处于积极开发和面向 v2 的重构阶段，可能存在 bug 或不稳定的 API，请谨慎使用。更多细节请查看我们的 [路线图](#roadmap)。也欢迎提出反馈和建议，或者直接提 issue / [联系我们](#contact-and-citations)。

## 为什么选择 bpftime？设计目标是什么？

- **性能提升**：通过 `绕过内核` 来获得更好的性能，例如借助 `Userspace DBI` 或 `Network Drivers`；同时提供更可配置、优化更强、架构支持更广的 JIT/AOT 选项，例如 `LLVM`，并保持与 Linux kernel eBPF 的兼容性。
- **跨平台兼容性**：在 kernel eBPF 不可用的场景下，例如旧版操作系统、其他操作系统，或者内核级权限受限时，仍可启用 `eBPF 功能及其庞大生态`，而无需修改你的工具。
- **灵活且通用的扩展语言与 runtime，支持创新**：eBPF 的设计初衷就是面向创新，并在生产环境中演化为一种通用扩展语言与 runtime，适用于非常多样化的场景。`bpftime` 的模块化设计让它能够很容易作为库集成，用于增加新的 events 和程序类型，而无需改动内核。我们希望它能帮助快速原型验证与探索新特性！

## 主要特性

- **动态二进制重写**：在用户态运行 eBPF 程序，并将其挂载到 `Uprobe`、`Syscall tracepoints` 以及 `GPU` kernel 中：**无需手动插桩或重启！** 它可以安全而高效地使用 eBPF 用户态 runtime 去 `trace` 或 `修改` 函数执行，`hook` 或 `filter` 一个进程的所有 syscall。无需重启或手动重新编译，就能把 eBPF runtime 注入到任意正在运行的进程中。
- **性能**：与 kernel uprobe 和 uretprobe 相比，Uprobe 开销最高可提升 `10x`；也可比 `NVbit` 快最多 10 倍。读写用户态内存的速度也比 kernel eBPF 更快。
- **进程间 eBPF Map**：在共享用户态内存中实现用户态 `eBPF maps`，用于汇总聚合或控制面通信。
- **兼容性**：使用 `clang`、`libbpf` 和 `bpftrace` 等 `现有 eBPF 工具链`，无需任何修改即可开发用户态 eBPF 应用。支持通过 BTF 提供 CO-RE，并提供用户态 `ufunc` 访问。
- **多 JIT 支持**：支持 [llvmbpf](https://github.com/eunomia-bpf/llvmbpf)，这是一个由 LLVM 驱动的高速 `JIT/AOT` 编译器；也支持 `ubpf JIT` 和解释器。该 vm 还能像 ubpf 一样被构建成 `独立库`。
- **与 kernel eBPF 协同运行**：可以从内核加载用户态 eBPF，并使用 kernel eBPF maps 与 kprobe、网络过滤器等内核 eBPF 程序协作。
- **与 AF_XDP 或 DPDK 集成**：像在内核中一样，在用户态以更高性能运行你的 `XDP` 网络应用（实验性）。

## 组件

- [`vm`](https://github.com/eunomia-bpf/bpftime/tree/master/vm)：bpftime 的 eBPF VM 和 JIT 编译器，可在 [bpftime LLVM JIT/AOT compiler](https://github.com/eunomia-bpf/llvmbpf) 与 [ubpf](https://github.com/iovisor/ubpf) 之间选择。bpftime 中基于 LLVM 的 vm 也可以像 ubpf 一样被构建为独立库并集成到其他项目中。
- [`runtime`](https://github.com/eunomia-bpf/bpftime/tree/master/runtime)：bpftime 的用户态 runtime，包含 maps、helpers、ufuncs 和其他 runtime 安全特性。
- [`Attach events`](https://github.com/eunomia-bpf/bpftime/tree/master/attach)：支持通过 bpf_link 将 eBPF 程序挂载到 `Uprobe`、`Syscall tracepoints`、`XDP` 等事件以及驱动事件源上。
- [`verifier`](https://github.com/eunomia-bpf/bpftime/tree/master/bpftime-verifier)：支持使用 [PREVAIL](https://github.com/vbpf/ebpf-verifier) 作为用户态 verifier，也支持使用 `Linux kernel verifier` 获得更好的结果。
- [`Loader`](https://github.com/eunomia-bpf/bpftime/tree/master/runtime/syscall-server)：包含一个用户态的 `LD_PRELOAD` loader library，可与当前 eBPF 工具链和库配合工作而无需依赖内核；如果 Linux eBPF 可用，也可以使用 [daemon](https://github.com/eunomia-bpf/bpftime/tree/master/daemon)。

## 快速开始：Uprobe

使用 `bpftime`，你可以通过 clang 和 libbpf 等熟悉的工具构建 eBPF 应用，并在用户态执行。例如，[`malloc`](https://github.com/eunomia-bpf/bpftime/tree/master/example/malloc) 这个 eBPF 程序会通过 uprobe 跟踪 malloc 调用，并使用 hash map 聚合计数。

关于如何构建项目，你可以参考 [eunomia.dev/bpftime/documents/build-and-test](https://eunomia.dev/bpftime/documents/build-and-test) 或仓库中的 `installation.md`。你也可以使用 [GitHub packages](https://github.com/eunomia-bpf/bpftime/pkgs/container/bpftime) 里的容器镜像。

要开始使用，你可以构建并运行一个基于 libbpf 的 eBPF 程序，使用 `bpftime` cli：

```console
make -C example/malloc # 构建 eBPF 示例程序
export PATH=$PATH:~/.bpftime/
bpftime load ./example/malloc/malloc
```

在另一个 shell 中，运行带有 eBPF 的目标程序：

```console
$ bpftime start ./example/malloc/victim
Hello malloc!
malloc called from pid 250215
continue malloc...
malloc called from pid 250215
```

你应当始终先运行 `load`，再运行 `start` 命令，否则 eBPF 程序不会被挂载。

你也可以把 eBPF 程序动态挂载到一个正在运行的进程上：

```console
$ ./example/malloc/victim & echo $! # pid 是 101771
[1] 101771
101771
continue malloc...
continue malloc...
```

然后把它 attach 上去：

```console
$ sudo bpftime attach 101771 # 你可能需要以 root 执行 make install
Inject: "/root/.bpftime/libbpftime-agent.so"
Successfully injected. ID: 1
```

你可以看到原始程序的输出：

```console
$ bpftime load ./example/malloc/malloc
...
12:44:35 
        pid=247299      malloc calls: 10
        pid=247322      malloc calls: 10
```

另外，你也可以直接在 kernel eBPF 中运行我们的示例 eBPF 程序，以观察相似的输出。这也可以说明 bpftime 如何与 kernel eBPF 保持兼容。

```console
$ sudo example/malloc/malloc
15:38:05
        pid=30415       malloc calls: 1079
        pid=30393       malloc calls: 203
        pid=29882       malloc calls: 1076
        pid=34809       malloc calls: 8
```

更多细节请参见 [eunomia.dev/bpftime/documents/usage](https://eunomia.dev/bpftime/documents/usage)。

## 示例与使用场景

更多示例和细节请查看 [eunomia.dev/bpftime/documents/examples/](https://eunomia.dev/bpftime/documents/examples/) 页面以及 [example](https://github.com/eunomia-bpf/bpftime/tree/master/example/) 目录。

## 深入了解

### **工作原理**

bpftime 支持两种模式：

#### 仅在用户态运行

左侧：原始 kernel eBPF | 右侧：bpftime

![How it works](https://eunomia.dev/bpftime/documents/bpftime.png)

在这种模式下，bpftime 可以在没有内核的情况下于用户态运行 eBPF 程序，因此它可以移植到较低版本的 Linux，甚至其他系统，并且不需要 root 权限。它依赖 [userspace verifier](https://github.com/vbpf/ebpf-verifier) 来确保 eBPF 程序的安全性。

#### 与 kernel eBPF 一起运行

![documents/bpftime-kernel.png](https://eunomia.dev/bpftime/documents/bpftime-kernel.png)

在这种模式下，bpftime 可以与 kernel eBPF 一起运行。它可以从内核加载 eBPF 程序，并使用 kernel eBPF maps 与 kprobe 和网络过滤器等内核 eBPF 程序协作。

#### 插桩实现

当前的 hook 实现基于二进制重写，其底层技术参考了以下工作：

- 用户态函数 hook：[frida-gum](https://github.com/frida/frida-gum)
- Syscall hook：[zpoline](https://www.usenix.org/conference/atc23/presentation/yasukata) 和 [pmem/syscall_intercept](https://github.com/pmem/syscall_intercept)
- GPU hook：通过将 eBPF 转换为 PTX 并注入到 GPU kernel 中的全新实现。更多细节请参见 [attach/nv_attach_impl](https://github.com/eunomia-bpf/bpftime/tree/master/attach/nv_attach_impl)
- 结合 DPDK 的 XDP。更多细节请参见 [uXDP paper](https://dl.acm.org/doi/10.1145/3748355.3748360)

这个 hook 可以很容易地替换为其他 DBI 方法或框架，从而把它做成一个通用扩展框架。更多细节请参见我们的 OSDI '25 论文 [Extending Applications Safely and Efficiently](https://www.usenix.org/conference/osdi25/presentation/zheng-yusheng)。

### **性能基准**

关于我们如何评估以及更多细节，请参见 [github.com/eunomia-bpf/bpf-benchmark](https://github.com/eunomia-bpf/bpf-benchmark)。

### 与 Kernel eBPF Runtime 对比

- `bpftime` 允许你使用 `clang` 和 `libbpf` 来构建 eBPF 程序，并像普通 kernel eBPF 一样直接在这个 runtime 中运行。我们已经使用 [third_party/libbpf](https://github.com/eunomia-bpf/bpftime/tree/master/third_party/libbpf) 中的 libbpf 版本做过测试，不需要特定的 libbpf 或 clang 版本。
- 某些 kernel helpers 和 kfuncs 在用户态中可能不可用。
- 它不支持直接访问内核数据结构或函数，例如 `task_struct`。

更多细节请参见 [eunomia.dev/bpftime/documents/available-features](https://eunomia.dev/bpftime/documents/available-features)。

## 构建与测试

详情请参见 [eunomia.dev/bpftime/documents/build-and-test](https://eunomia.dev/bpftime/documents/build-and-test)。

## 许可证

本项目采用 MIT License。

## 联系方式与引用

如果你对未来发展有任何问题或建议，欢迎提 issue 或联系
<yunwei356@gmail.com>！

我们的 OSDI '25 论文：<https://www.usenix.org/conference/osdi25/presentation/zheng-yusheng>

```txt
@inproceedings{zheng2025extending,
  title={Extending Applications Safely and Efficiently},
  author={Zheng, Yusheng and Yu, Tong and Yang, Yiwei and Hu, Yanpeng and Lai, Xiaozheng and Williams, Dan and Quinn, Andi},
  booktitle={19th USENIX Symposium on Operating Systems Design and Implementation (OSDI 25)},
  pages={557--574},
  year={2025}
}
```

## 致谢

eunomia-bpf 社区由来自 [ISCAS](http://english.is.cas.cn/au/) 的 [PLCT Lab](https://plctlab.github.io/) 赞助。

也感谢其他赞助方以及在这个项目建设过程中提供讨论帮助的人：来自 Imperial College London 的 [Prof. Marios Kogias](https://marioskogias.github.io/)，来自 SCUT 的 [Prof. Xiaozheng lai](https://www2.scut.edu.cn/cs/2017/0129/c22285a327654/page.htm)，来自 XUPT 的 [Prof lijun chen](http://www.xiyou.edu.cn/info/2394/67845.htm)，来自 THU [NISL Lab](https://netsec.ccert.edu.cn/en/) 的 [Prof. Qi Li](https://sites.google.com/site/qili2012/)，以及 LPC 23 eBPF track 的 Linux eBPF 维护者们。
