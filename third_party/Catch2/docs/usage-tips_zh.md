<a id="top"></a>
# 使用 Catch2 的最佳实践与其他提示

## 运行测试

你的测试应该以大致如下的方式运行：

```text
./tests --order rand --warn NoAssertions
```

注意，所有测试都作为一个大批次运行，它们的相对顺序是随机的，而且你要求 Catch2 让那些叶子路径中没有断言的测试失败。

我之所以建议把所有测试放在同一个进程里运行，是因为这样可以暴露测试之间的相互影响。这种影响既可能是正向的，也就是前一个测试改变了全局状态，从而让后面的测试通过；也可能是负向的，也就是前一个测试改变了全局状态，从而让后面的测试失败。

根据我的经验，这种相互影响，尤其是破坏性的相互影响，通常来自被测代码中的错误，而不是测试本身。这意味着，允许这种影响发生，反而能帮助我们的测试发现问题。显然，为了找出不同测试顺序带来的影响，测试顺序也需要在不同运行之间随机打乱。

不过，把所有测试一次性放在单个批次里运行，最终会变得不现实，因为它们会耗时太久，这时你就会想把测试并行运行。

<a id="parallel-tests"></a>
## 并行运行测试

并行运行测试有多种方式，结构化程度也各不相同。如果你使用 CMake 和 CTest，那么我们提供了一个辅助函数 [`catch_discover_tests`](docs/docs/cmake-integration_zh.md#automatic-test-registration)，它会把每个 Catch2 `TEST_CASE` 注册为一个独立的 CTest 测试，然后由单独进程运行。如果你已经在用 CMake 和 CTest 跑测试，这是一种很方便的并行测试设置方式，但你会失去批量运行测试的优势。

Catch2 也支持[把二进制中的测试拆分成多个 shard](docs/docs/command-line_zh.md#test-sharding)。任何测试运行器都可以利用这一点，把测试批次并行执行。需要注意的是，在选择 shard 数量时，应该让 shard 数量大于核心数，以避免长时间运行的测试意外被分到同一个 shard，从而导致执行时间出现长尾。

**注意，简单地把 sharding 和随机顺序组合起来会出问题。**

像这样调用 Catch2 测试可执行文件：

```text
./tests --order rand --shard-index 0 --shard-count 3
./tests --order rand --shard-index 1 --shard-count 3
./tests --order rand --shard-index 2 --shard-count 3
```

并不能保证覆盖可执行文件中的所有测试，因为每次调用都会有自己的随机种子，因此也会有自己的测试随机顺序，测试在各个 shard 中的划分也会随之改变。

正确做法是让各个 shard 共享同一个随机种子，例如：

```text
./tests --order rand --shard-index 0 --shard-count 3 --rng-seed 0xBEEF
./tests --order rand --shard-index 1 --shard-count 3 --rng-seed 0xBEEF
./tests --order rand --shard-index 2 --shard-count 3 --rng-seed 0xBEEF
```

Catch2 实际上提供了一个辅助功能，可以自动把多个 shard 注册为 CTest 测试，并让它们共享随机种子，而随机种子会在每次 CTest 调用时变化。详情请看 [`CatchShardTests.cmake` CMake 脚本](docs/docs/cmake-integration_zh.md#catchshardtestscmake) 的文档。

## 将测试组织到不同二进制中

过大的测试二进制和过小的测试二进制都会带来问题。过大的测试二进制需要频繁重新编译和重新链接，而且链接时间通常也很长。过小的测试二进制则会在每个编译后的测试用例上，更多次地付出链接 Catch2 的显著开销，同时也会让批量运行测试变得困难甚至不可能。

由于测试二进制的最佳大小没有绝对规则，我建议让项目中的库和测试二进制保持 1:1 对应关系。（至少在可行时如此，有些情况下做不到。）为项目中的每个库都准备一个测试二进制，可以把相关测试放在一起，也能通过反映项目组织结构来让测试更容易导航。

---

[Home](Readme_zh.md#top)
