# bpftime Attach System

bpftime 的 attach system 提供了一个模块化框架，用于在用户态把 eBPF 程序挂载到各种事件源上。它支持多种挂载类型，包括函数探针（uprobes）、syscall 跟踪，以及 CUDA kernel 插桩等专用挂载。

## 架构概览

### 核心设计原则

1. **模块化设计**：每种 attach 类型都实现为一个独立模块，并继承自 `base_attach_impl`
2. **统一接口**：所有 attach 实现都遵循相同的接口模式，以保持一致性
3. **可扩展性**：通过实现 base 接口，可以很容易增加新的 attach 类型
4. **跨进程支持**：attach 点可以通过共享内存在进程间共享

### 组件结构

```
attach/
├── base_attach_impl/           # 基础接口与通用功能
├── frida_uprobe_attach_impl/   # 使用 Frida 做函数插桩
├── syscall_trace_attach_impl/  # 系统调用跟踪
├── nv_attach_impl/             # CUDA/GPU kernel 插桩
├── simple_attach_impl/         # 简化版 attach 封装
└── text_segment_transformer/   # 用于 syscall 拦截的二进制重写
```

## 基础接口

`base_attach_impl` 类定义了所有 attach 实现必须遵循的核心接口：

```cpp
class base_attach_impl {
public:
    // 按 ID 解除一个 attachment
    virtual int detach_by_id(int id) = 0;
    
    // 使用 eBPF 回调创建 attachment
    virtual int create_attach_with_ebpf_callback(
        ebpf_run_callback &&cb, 
        const attach_private_data &private_data,
        int attach_type) = 0;
    
    // 注册自定义 helper 函数
    virtual void register_custom_helpers(
        ebpf_helper_register_callback register_callback);
    
    // 调用 attach 特定功能
    virtual void *call_attach_specific_function(
        const std::string &name, void *data);
};
```

### 关键类型

- **`ebpf_run_callback`**：在准备好上下文后执行 eBPF program 的函数
- **`attach_private_data`**：attach 特定配置数据的基类
- **`override_return_set_callback`**：用于修改返回值的线程局部回调

## Attach 实现

### 1. Frida Uprobe Attach（`frida_uprobe_attach_impl`）

提供基于 Frida-gum 框架的动态函数插桩。

**特性：**
- 函数入口探针（uprobe）
- 函数返回探针（uretprobe）
- override 探针（修改函数行为）
- 函数替换（ureplace）

**Attach 类型：**
- `ATTACH_UPROBE`（6）：在函数入口执行
- `ATTACH_URETPROBE`（7）：在函数返回时执行
- `ATTACH_UPROBE_OVERRIDE`（1008）：覆盖函数行为
- `ATTACH_UREPLACE`（1009）：完全替换函数

**关键组件：**
- 通过 `pt_regs` 捕获寄存器状态
- 为不同探针场景提供多种回调类型
- 线程局部 CPU 上下文管理

### 2. Syscall Trace Attach（`syscall_trace_attach_impl`）

在没有内核支持的情况下拦截并跟踪系统调用。

**特性：**
- 跟踪 syscall 入口和出口
- 按 syscall 或全局回调
- 极低的性能开销

**关键组件：**
- `trace_event_raw_sys_enter/exit`：与 eBPF 兼容的事件结构
- 最多支持 512 个 syscall 槽位的调度器
- 与 text segment transformer 集成以实现拦截

**流程：**
1. text segment transformer hook syscall 指令
2. hook 重定向到 `dispatch_syscall`
3. dispatcher 调用注册的 eBPF 程序
4. 若未被覆盖，则执行原始 syscall

### 3. CUDA Attach（`nv_attach_impl`）

对 CUDA kernel 和 GPU 操作进行插桩（仅 Linux）。

**特性：**
- 内存操作捕获
- kernel 函数探针/返回探针
- PTX 代码转换
- eBPF 到 PTX 的编译

**Attach 类型：**
- `ATTACH_CUDA_PROBE`（8）：CUDA kernel 入口
- `ATTACH_CUDA_RETPROBE`（9）：CUDA kernel 退出

**实现：**
1. 拦截 CUDA runtime API
2. 提取并修改 PTX 代码
3. 将 eBPF 程序注入为 PTX
4. 重新编译并加载修改后的 kernel

### 4. Simple Attach（`simple_attach_impl`）

为自定义事件源提供简化 attach 接口的封装。

**特性：**
- 单回调模型
- 基于字符串的配置
- 易于集成新的事件类型

**使用场景：**
适合原型验证新的 attach 类型，或者不需要复杂上下文准备的简单事件源。

## 私有数据系统

每种 attach 类型都会定义自己的 `attach_private_data` 子类：

```cpp
struct attach_private_data {
    virtual int initialize_from_string(const std::string_view &sv);
    virtual std::string to_string() const;
};
```

示例：
- `frida_attach_private_data`：函数地址、偏移、模块信息
- `syscall_trace_private_data`：syscall 编号、入口/出口标志
- `nv_attach_private_data`：kernel 名称、attach 类型

## Helper 函数

attach 实现可以注册自定义 helper 函数：

```cpp
// 所有 attach 类型都可用的全局 helper
bpftime_set_retval()      // 设置函数返回值
bpftime_override_return()  // 用指定值覆盖返回

// 通过 register_custom_helpers() 注册的 attach 特定 helper
```

## 线程安全

- 每种 attach 实现都负责自己的同步
- 使用线程局部存储保存每线程状态（例如 override 回调）
- 需要时，shared memory 操作会使用原子语义

## 添加新的 Attach 类型

1. 在 `attach/` 下创建新目录
2. 继承 `base_attach_impl`
3. 实现要求的虚函数
4. 如有需要，定义自定义 `attach_private_data`
5. 添加到 `CMakeLists.txt`
6. 在 runtime 中注册 attach type ID

## 平台支持

- **Linux**：支持所有 attach 类型
- **macOS**：仅限基于 Frida 的 attachment
- **Windows**：当前不支持

特殊要求：
- CUDA attach 需要 NVIDIA GPU 和 CUDA toolkit
- Syscall trace 需要 text segment 修改权限
- 某些特性可能需要 root / 提权

## 性能考虑

1. **Frida Uprobe**：每次探针约 10-100ns 开销
2. **Syscall Trace**：未跟踪 syscall 的开销极小
3. **CUDA Attach**：开销取决于 kernel 复杂度
4. **Simple Attach**：取决于回调实现

## 与 runtime 集成

attach system 通过以下方式与 bpftime runtime 集成：
- 通过 handler manager 管理对象生命周期
- 通过 shared memory 实现跨进程访问
- 通过 VM interface 执行 eBPF 程序
- 通过 helper function registration system 注册 helper 函数
