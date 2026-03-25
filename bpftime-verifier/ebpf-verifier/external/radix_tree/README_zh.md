
radix_tree
=====

[![Build Status](https://travis-ci.org/ytakano/radix_tree.svg?branch=master)](https://travis-ci.org/ytakano/radix_tree)

C++ 中类似 STL 的 radix tree 容器

使用方法
=====
这是一个仅头文件库。直接包含即可。参见 [examples](examples/)。

开发
=====
要求：任何 C++98 编译器（`g++` 或 `clang++`）、`cmake`

```
~/radix_tree $ mkdir build && cd build
~/radix_tree/build $ cmake .. -DBUILD_TESTS=On
~/radix_tree/build $ make check
```

版权
=====
参见 [COPYING](COPYING)。
