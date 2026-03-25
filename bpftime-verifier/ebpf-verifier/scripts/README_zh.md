## 性能评估

要进行性能测试，请运行：
```
scripts/runperf.sh ebpf-samples stats zoneCrab | tee results.csv
```
脚本的第一个参数 `ebpf-samples` 是搜索 elf 文件的根目录。你也可以传入任意子目录或文件，例如
`ebpd-samples/linux`。

其余位置参数是要使用的数值域。

输出是一个很大的 `csv` 文件。第一行是表头：
```
suite,project,file,section,hash,instructions,loads,stores,jumps,joins,zoneCrab?,zoneCrab_sec,zoneCrab_kb
ebpf-samples,cilium,bpf_lxc.o,2/1,69a5e4fc57ca1c94,41,6,10,1,1,1,0.057409,21796
```
* _suite_ 在这里将是 "ebpf-samples"
* _project_ 是 suite 下的目录之一。当前包含 `bpf_cilium_test`、`cilium`、`linux`、`ovs`、`prototype-kernel` 和 `suricata`
* _file_ 是包含程序的 elf 文件。C 文件编译后的版本
* _section_ 是被检查的 elf section
* _hash_ 是 eBPF 代码的唯一哈希。基准中存在重复程序（因为我们按原样使用了这些项目中的文件）。要统计真实的程序数量，应去掉这些重复项
* _instructions_、_loads_、_stores_、_jumps_ 和 _joins_ 表示这些特征的数量
* 对于每个域 DOM，会有 3 列连续的列：
    * "DOM?" 为 0 表示程序被拒绝，1 表示程序被接受
    * "DOM_sec" 表示 fixpoint 操作耗时（秒）
    * "DOM_kb" 表示分析所消耗的峰值 resident set size，是分析所需额外内存的大致估计
