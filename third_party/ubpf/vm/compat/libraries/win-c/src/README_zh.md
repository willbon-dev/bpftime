win-c
============

这是一个可供 C/C++ 使用的 Windows 控制台应用程序库。

__函数__

* `getopt() / getopt_long()` - 命令行选项解析

## `getopt() / getopt_long()` - 命令行选项解析

函数规范请参考 [POSIX getopt](http://linuxjm.sourceforge.jp/html/LDP_man-pages/man3/getopt.3.html)。

* 不支持长选项的 `optional_argument`，也不支持 `getopt_long_only()`。

### 使用示例

下面是一个 C++ 中的使用示例。

```
#include <iostream>
#include "getopt.h"
using namespace std;
int main(int argc, char* argv[]) {
    // 选项定义。a, b, c, d，其中 b 和 c 需要参数
    //  -a
    //  -b <opt_b_arg>
    //  -c <opt_c_arg>
    //  -d
    char const * optstring = "ab:c:d";
    int opt_a = 0;
    char* opt_b = 0;
    char* opt_c = 0;
    int opt_d = 0;

    // 解析选项
    int opt = 0;
    while((opt = getopt(argc, argv, optstring)) != -1) {
        switch(opt) {
        case 'a':
            opt_a = 1;
            break;
        case 'b':
            opt_b = optarg;
            break;
        case 'c':
            opt_c = optarg;
            break;
        case 'd':
            opt_d = 1;
            break;
        default:
            cerr << "unknown option." << endl;
            exit(-1);
            break;
        }
    }

    // 非选项参数
    char* noptarg = argv[optind++];
}
```

### 使い方

把 main 函数的 argc、argv 和选项定义字符串传进去，重复调用直到返回 `-1`，即可完成选项解析。

#### 选项定义

选项通过把各个选项字符拼成的字符串来定义。

需要参数的选项，在选项字符后面加一个冒号。

#### 返回值

`-1` 表示选项解析结束。

找到一个选项时，返回对应字符。

如果传入了不是选项的字符，则返回 `'?'`。

#### 选项参数

当找到一个需要参数的选项时，`optarg` 会指向它的参数。

#### 非选项命令行参数

选项解析结束后，全局变量 `optind` 会指向第一个非选项命令行参数。
如果 `optind < argc`，那么 `argv[optind]` 就是第一个非选项命令行参数。
如果 `optind >= argc`，则说明没有非选项参数。
