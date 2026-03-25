# bpftimetool

用于检查和管理 bpftime 共享内存状态的命令行工具。

## 概览

`bpftimetool` 提供以下能力：
- 将共享内存状态导出为 JSON，便于检查或备份
- 把 JSON 中的 eBPF 对象导入到共享内存
- 以性能基准测试方式运行 eBPF 程序
- 删除系统范围内的共享内存段

## 安装

构建 bpftime 后，工具位于：
```bash
~/.bpftime/bpftimetool
# 或加入 PATH
export PATH=$PATH:~/.bpftime/
```

## 命令参考

### export - 将共享内存导出为 JSON

```bash
bpftimetool export <filename>
```

### import - 将 JSON 加载到共享内存

```bash
bpftimetool import <filename>
```

### run - 执行并基准测试程序

```bash
bpftimetool run <id> <data_file> [repeat N] [type RUN_TYPE]
```

### remove - 清理共享内存

```bash
bpftimetool remove
```

## 常见工作流

### 调试工作流

### 性能分析工作流

### 备份与恢复

### 跨系统测试

## JSON 格式

## Handler 类型

## 环境变量

## 故障排查

## 性能说明

## 与 bpftime 集成

## 另见
