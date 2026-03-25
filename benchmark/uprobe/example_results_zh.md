# BPFtime Uprobe 基准结果

*生成于 2025-04-30 03:01:13*

## 环境

- **操作系统：** Linux 6.11.0-24-generic
- **CPU：** Intel(R) Core(TM) Ultra 7 258V（4 核，4 线程）
- **内存：** 15.07 GB
- **Python：** 3.12.7

## 总结

这个基准测试比较了三种不同的 eBPF 执行环境：
- **内核 Uprobe**：传统的基于内核的 eBPF uprobe
- **用户态 Uprobe**：BPFtime 的用户态 uprobe 实现
- **嵌入式 VM**：BPFtime 的嵌入式 eBPF VM

*时间单位均为纳秒（ns），越小越好*

### 核心 Uprobe 性能汇总

| Operation | Kernel Uprobe | Userspace Uprobe | Speedup |
|-----------|---------------|------------------|---------|
| __bench_uprobe | 2561.57 | 190.02 | 13.48x |
| __bench_uretprobe | 3019.45 | 187.10 | 16.14x |
| __bench_uprobe_uretprobe | 3119.28 | 191.63 | 16.28x |

### 内核与用户态 eBPF 的详细对比

| Operation | Environment | Min (ns) | Max (ns) | Avg (ns) | Std Dev |
|-----------|-------------|----------|----------|----------|---------|
| __bench_array_map_delete | Kernel | 2725.99 | 3935.98 | 3237.62 | 359.11 |
| __bench_array_map_delete | Userspace | 2909.07 | 3285.52 | 3096.46 | 114.99 |
| __bench_array_map_lookup | Kernel | 2641.18 | 4155.25 | 2992.88 | 402.00 |
| __bench_array_map_lookup | Userspace | 3354.17 | 3724.05 | 3486.81 | 108.63 |
| __bench_array_map_update | Kernel | 9945.97 | 14917.03 | 12225.93 | 1508.60 |
| __bench_array_map_update | Userspace | 4398.82 | 4841.92 | 4629.57 | 152.57 |
| __bench_hash_map_delete | Kernel | 18560.92 | 27069.99 | 22082.68 | 2295.90 |
| __bench_hash_map_delete | Userspace | 9557.35 | 11240.72 | 10253.54 | 473.67 |
| __bench_hash_map_lookup | Kernel | 10181.58 | 13742.86 | 12375.69 | 1142.61 |
| __bench_hash_map_lookup | Userspace | 20580.46 | 23586.77 | 22152.81 | 969.63 |
| __bench_hash_map_update | Kernel | 43969.13 | 61331.16 | 53376.22 | 5497.51 |
| __bench_hash_map_update | Userspace | 21172.05 | 25878.44 | 23992.67 | 1264.81 |
| __bench_per_cpu_array_map_delete | Kernel | 2782.47 | 3716.44 | 3183.09 | 287.23 |
| __bench_per_cpu_array_map_delete | Userspace | 2865.53 | 3409.70 | 3114.67 | 140.65 |
| __bench_per_cpu_array_map_lookup | Kernel | 2773.47 | 4176.10 | 3170.42 | 416.42 |
| __bench_per_cpu_array_map_lookup | Userspace | 6269.58 | 7395.49 | 7018.47 | 345.91 |
| __bench_per_cpu_array_map_update | Kernel | 10662.37 | 15923.08 | 12326.39 | 1522.21 |
| __bench_per_cpu_array_map_update | Userspace | 15592.15 | 17505.63 | 16528.99 | 553.50 |
| __bench_per_cpu_hash_map_delete | Kernel | 19709.29 | 26844.96 | 21994.95 | 2243.80 |
| __bench_per_cpu_hash_map_delete | Userspace | 55954.89 | 76124.07 | 65603.07 | 5986.58 |
| __bench_per_cpu_hash_map_lookup | Kernel | 10783.48 | 15208.46 | 12315.21 | 1525.86 |
| __bench_per_cpu_hash_map_lookup | Userspace | 48033.46 | 57481.09 | 50651.83 | 2503.34 |
| __bench_per_cpu_hash_map_update | Kernel | 31072.46 | 43163.81 | 35580.60 | 3748.51 |
| __bench_per_cpu_hash_map_update | Userspace | 73661.69 | 79157.12 | 76526.24 | 1868.13 |
| __bench_read | Kernel | 22506.85 | 30934.20 | 25865.43 | 3018.32 |
| __bench_read | Userspace | 1491.75 | 1862.13 | 1653.45 | 101.66 |
| __bench_uprobe | Kernel | 2130.54 | 4389.26 | 2561.57 | 628.77 |
| __bench_uprobe | Userspace | 166.54 | 232.13 | 190.02 | 16.11 |
| __bench_uprobe_uretprobe | Kernel | 2658.28 | 3859.19 | 3119.28 | 311.45 |
| __bench_uprobe_uretprobe | Userspace | 179.61 | 202.69 | 191.63 | 9.64 |
| __bench_uretprobe | Kernel | 2581.48 | 3916.19 | 3019.45 | 359.75 |
| __bench_uretprobe | Userspace | 175.54 | 196.49 | 187.10 | 7.66 |
| __bench_write | Kernel | 22783.52 | 31415.49 | 26478.92 | 2787.90 |
| __bench_write | Userspace | 1406.01 | 1802.50 | 1542.49 | 106.23 |

### 嵌入式 VM 性能

| Operation | Min (ns) | Max (ns) | Avg (ns) | Std Dev |
|-----------|----------|----------|----------|---------|
| embed | 75.47 | 221.55 | 106.30 | 39.99 |

## 基准元数据

- **运行次数：** 10
- **时间戳：** 2025-04-30 03:01:13
- **总耗时：** 559.80 秒
