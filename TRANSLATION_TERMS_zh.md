# bpftime 文档翻译术语表

本文件用于统一仓库内 Markdown 中文副本的术语译法与保留规则。

## 保留英文

以下术语默认保留英文，不做中文翻译：

- `eBPF`
- `BPF Map`
- `Uprobe`
- `Uretprobe`
- `USDT`
- `XDP`
- `JIT`
- `AOT`
- `LLVM`
- `libbpf`
- `bpftrace`
- `BTF`
- `CO-RE`
- `helper`
- `kfunc`
- `hook`
- `runtime`
- `loader`
- `verifier`
- `daemon`
- `benchmark`
- `CLI`
- `API`
- `ABI`
- `ELF`
- `PTX`
- `SPIR-V`
- `GPU`
- `CPU`
- `DPDK`
- `AF_XDP`
- `syscall`
- `tracepoint`
- `uprobes`
- `kprobes`
- `LD_PRELOAD`
- `ring buffer`
- `shared memory`

## 推荐译法

- userspace -> 用户态
- kernel -> 内核
- userspace eBPF runtime -> 用户态 eBPF runtime
- general extension framework -> 通用扩展框架
- observability -> 可观测性
- attach -> 挂载
- dynamic binary rewriting -> 动态二进制重写
- compatibility -> 兼容性
- standalone library -> 独立库
- code coverage -> 代码覆盖率
- instruction set -> 指令集
- build system -> 构建系统
- contributing -> 贡献指南
- code of conduct -> 行为准则
- security policy -> 安全策略
- governance -> 治理规范
- development guide -> 开发指南
- release notes -> 发布说明
- issue template -> Issue 模板
- pull request template -> Pull Request 模板

## 翻译规则

- 保留原始 Markdown 结构，包括标题、列表、表格、代码块、图片、徽章、HTML 片段和引用。
- 命令、路径、环境变量、代码标识符、配置项、提交号、版本号、API 名称保持原文。
- 相对 `.md` 链接优先改为对应的 `_zh.md` 文件；若目标没有中文副本，则保留原链接。
- 引用文本可以翻译，但不要改动 URL。
- 不增加双语对照，不添加“机器翻译”之类的额外说明。
