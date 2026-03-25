# Argparse 测试

## Linux

```bash
$ mkdir build
$ cd build
$ cmake ../.
$ make
$ ./tests
```

## Windows

1. 生成 Visual Studio 解决方案

```bash
$ mkdir build
$ cd build
$ cmake ../. -G "Visual Studio 15 2017"
```

2. 打开 `ARGPARSE.sln`
3. 以 `RELEASE | x64` 构建测试
4. 运行 `tests.exe`
