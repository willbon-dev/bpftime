# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在处理本仓库代码时提供指引。

## 项目概览

llvmbpf 是一个高性能的用户态 eBPF VM，带有 LLVM JIT/AOT 编译器。它通过 LLVM IR 把 eBPF bytecode 编译成 native code，支持多架构执行（x86、ARM、NVPTX/CUDA），并且支持把 eBPF 程序 AOT 编译成独立的 native ELF 对象。

这是一个从 bpftime 项目中抽出来的独立 VM 库，只关注编译和执行，不包含 maps、helpers、verifiers 或 loaders。

## 构建命令

### 标准构建（Release）

### 带 AOT CLI 工具的构建

### 带 PTX/CUDA 支持的构建

### 带 SPIR-V/OpenCL 支持的构建

### 用于开发/测试的构建

## 测试

### 运行单元测试

### 运行 BPF Conformance 测试

### 运行示例程序

## 架构

### 核心组件

### LDDW Helpers 和 Maps

### 外部函数

### 编译模式

## CLI 工具用法

## 关键约束

## 与 bpftime 的集成

## 示例目录结构
