# ubpf-vm

这是一个对 ubpf 的封装，为 bpftime 提供统一接口。它还包含一些适配器，以便使用 ubpf 中缺少的某些特性：
- 由于 ubpf 只支持 64 个 helper，所以会把 helper id 重映射到 0-63
- 加载代码时会 patch lddw 指令
