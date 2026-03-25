# Text Segment Transformer

这个组件会修改进程的可执行代码（text segment），以便为 bpftime 拦截系统调用。

## 概览

Text Segment Transformer 会重写程序内存中的所有 `syscall` 指令，将它们重定向到自定义 handler。这样就可以在不修改内核的情况下，透明地拦截所有系统调用。

## 核心组件

- **Text Segment Transformer**：重写可执行内存以拦截 syscalls
- **Agent Transformer**：可以注入进程中的动态 agent，用于启用 syscall 拦截

## 工作方式

1. **内存映射**：transformer 会在地址 0x0 映射一个带执行权限的特殊页面
2. **代码重定向**：扫描进程中的所有可执行内存区域，并把 `syscall` 指令重写为跳转到 handler
3. **Syscall 分发**：当执行 syscall 时，它会被重定向到 handler 函数，handler 可以：
   - 处理 syscall 参数
   - 调用已注册的回调（例如 eBPF 程序）
   - 选择是否执行原始 syscall
   - 把结果返回给调用代码

## 架构细节

### 内存布局

transformer 会设置一种特殊的内存布局：
- 把第一页（0x0）映射为可执行
- 前半部分填充 NOP，以保留空指针解引用的行为
- 在已知偏移处放置一段跳转序列，把控制流重定向到 syscall handler

### Syscall Hook

当在可执行页面中找到 syscall 指令时，会把它替换为：
```asm
call rax  ; 通过寄存器跳转到 handler 的 call 指令
```

然后 handler 会：
1. 保存原始 syscall 参数
2. 把它们从 syscall ABI 转换成 C function call ABI
3. 调用 dispatch 函数
4. 再把结果转换回 syscall ABI 格式
5. 返回到原始代码

## 使用

使用 transformer 有两种方式：

### 1. 预加载方式

```bash
# 设置环境变量
export AGENT_SO=/path/to/bpftime-agent.so
LD_PRELOAD=/path/to/bpftime-agent-transformer.so your_program
```

### 2. Frida 注入

transformer 也可以使用 Frida 注入到正在运行的进程中。

## 与 Syscall Trace Attach 实现集成

Text Segment Transformer 与 Syscall Trace Attach 实现协同工作：

1. transformer 在指令级别拦截 syscalls
2. 它把它们重定向到 syscall handler
3. handler 调用 syscall trace 实现
4. 该实现再分发给注册的 eBPF 程序
5. 结果沿着调用链返回
