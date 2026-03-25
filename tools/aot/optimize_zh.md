# bpftime 中的优化级别与 runtime 配置

bpftime 主要有四种 runtime 配置：

- 解释器模式
- LLVM JIT
- ubpf JIT（simple jit）
- LLVM AOT

## LLVM JIT

这是 LLVM JIT 的基础配置。

- 从 eBPF bytecode 生成 LLVM IR。这个层面我们不会给 IR 增加类型信息，因此某些约束可能缺失，比如函数类型、循环边界、指针布局等。
- JIT 编译时使用 `-O3` 级别优化。
- 使用与 AOT runtime 相同的 linker 加载。

见 https://github.com/eunomia-bpf/bpftime/tree/master/vm/llvm-jit

## ubpf JIT

这是 ubpf JIT 的基础配置。

它是 bpftime 中对 ubpf JIT 的移植。

- 从 eBPF bytecode 生成 native instructions。
- 不做额外优化。
- 编译过程更快。

见 https://github.com/eunomia-bpf/bpftime/tree/master/vm/ubpf-vm

## LLVM AOT

bpftime AOT engine 可以把 eBPF bytecode 生成的 LLVM IR 编译成 `.o` 文件，也可以直接加载和检查预编译的 native object file 作为 AOT 结果。这有助于我们探索更好的优化方案。

linker（负责把 AOT 程序加载进 runtime）会检查：

- 函数和 helper 的类型是否正确
- stack 和 maps 布局是否正确
- runtime 中是否具备所有必要的 helper

AOT 的典型流程：

- eBPF 应用创建所有 maps、eBPF programs，并定义要使用的 helper 集合，这些信息存储在 shared memory 中。
- 在 runtime 的帮助下，eBPF 应用会完成 map id 或 BTF 的 relocation。
- verifier 检查 eBPF programs、maps 和 helpers。
- AOT compiler `#1` 把已验证的 eBPF programs 编译成 LLVM IR 和 native code，或者 `#2` 根据源代码中的类型信息，在 AST 层面做一些额外处理后，再编译成 LLVM IR 和 native code。
- AOTed object file 通过内置 linker 加载到 runtime 中，并可像其他 eBPF 程序一样执行。

AOT 流程会做：

- 使用 `-O3 -fno-stack-protector` 编译，确保 stack layout 正确。
- 把 eBPF program 的入口替换为函数名 `bpf_main`。
- 把所有 helper 替换为对应的类型信息和名称，例如 `_bpf_helper_ext_0001`。

AOT 中有三种优化：

- 添加类型信息，让 LLVM 做更好的优化。
  - 观察：eBPF bytecode 没有类型信息，所以如果我们只从 bytecode 做 JIT，LLVM 无法进行某些优化，比如 inline、loop unrolling、SIMD 等。加入类型信息后，LLVM 可以做出更好的优化。
  - 方案：在 LLVM IR 中添加类型信息，或者直接从源代码中获取。
- inline helpers。
  - 观察：某些 helper，例如复制数据、strcmp、计算 csum、生成随机值等都很简单，而且不会和其他 maps 交互。它们存在是为了 verifier 的限制。把它们 inline 掉可以避免函数调用开销，并让 LLVM 更容易优化。
  - 方案：准备一份用 C 或 LLVM IR 实现的 helper，并把它编译后与 AOT eBPF 结果链接。
- inline maps。
  - 观察：某些 maps 只是用于配置，一旦加载后，用户态程序不会再读它们；它们也不会在不同 eBPF 程序之间共享。例如 tracing 程序里的 `target_pid` filter，或者网络程序中的某些 config map。把它们 inline 可以避免 map lookup 的开销，并让 LLVM 更容易优化，因为 eBPF instruction 需要通过 helper 或 `__lddw_helper_map_by_fd` 之类的方式访问它们。
  - 方案：把 maps 以内联 global variables 的形式放入 native code，使 AOT linker 可以处理它们。linker 会把这些 `global variables` 在 runtime 中分配为真实的 global variables，并直接把 map access 替换成该 global variable 的地址。
