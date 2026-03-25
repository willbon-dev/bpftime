# 测试

## 如何运行？

- 在 `PROJECT_ROOT/vm` 中使用 `-DBPFTIME_LLVM_JIT=YES` 构建目标 `test_Tests`
- 使用 Python 3.8 创建 venv，然后安装 `vm/test/requirements.txt` 中的依赖
- 在 `vm/test/test_frameworks` 中运行 `pytest -k "test_jit.py and not err-infinite"`

## 预期结果

有些测试不预期成功。部分测试使用了我们尚未实现的特性，或者它们是为其他 runtime 的特定场景准备的。
