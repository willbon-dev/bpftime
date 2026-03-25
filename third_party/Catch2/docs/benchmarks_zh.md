<a id="top"></a>
# 编写 benchmark

> Catch2 2.9.0 中引入。

编写 benchmark 并不容易。Catch 能简化某些方面，但你仍然需要关注很多细节。理解 Catch 如何运行你的代码，对写 benchmark 会很有帮助。

先来看看本指南里会用到的一些术语。

- *User code*：用户提供、要被测量的代码。
- *Run*：一次 run 就是一次用户代码执行；有时也称为 _iteration_。
- *Sample*：一次 sample 是通过测量某个固定 run 次数所花费时间得到的一个数据点。如果可用时钟的分辨率不足以准确测量单次 run，一次 sample 可能包含不止一次 run。某次 benchmark 执行的所有 sample 都使用相同的 run 次数。

## 执行流程

Catch 中的 benchmark 执行流程可以分成三个主要步骤，不过第一个步骤不需要对每个 benchmark 都重复。

1. *环境探测*：在执行任何 benchmark 之前，会先估算时钟分辨率。在这一步还会估算一些其他环境因素，例如调用时钟函数的成本，但它们通常不会对结果造成影响。

2. *估算*：用户代码会先执行几次，以估算每个 sample 应该包含多少次 run。这一步还有可能把相关代码和数据提前带入缓存，以便真正测量时受益。

3. *测量*：随后会按顺序收集所有 sample，每个 sample 都按前一步估算出的 run 次数执行。

这已经给了我们一个写 Catch benchmark 的重要规则：benchmark 必须可重复执行。用户代码会被执行多次，而估算阶段具体会执行多少次，事先并不知道，因为它取决于代码本身的执行时间。不能重复执行的用户代码会导致错误结果甚至崩溃。

## Benchmark 规格

Benchmark 可以写在 Catch 测试用例里的任何地方。`BENCHMARK` 宏有一个简单版本和一个稍微高级一点的版本。

先看一个朴素 Fibonacci 实现怎么做 benchmark：
```c++
std::uint64_t Fibonacci(std::uint64_t number) {
    return number < 2 ? 1 : Fibonacci(number - 1) + Fibonacci(number - 2);
}
```
最直接的方式就是把 `BENCHMARK` 宏加到测试用例里：
```c++
TEST_CASE("Fibonacci") {
    CHECK(Fibonacci(0) == 1);
    // some more asserts..
    CHECK(Fibonacci(5) == 8);
    // some more asserts..

    // now let's benchmark:
    BENCHMARK("Fibonacci 20") {
        return Fibonacci(20);
    };

    BENCHMARK("Fibonacci 25") {
        return Fibonacci(25);
    };

    BENCHMARK("Fibonacci 30") {
        return Fibonacci(30);
    };

    BENCHMARK("Fibonacci 35") {
        return Fibonacci(35);
    };
}
```
这里有几点需要注意：
- 由于 `BENCHMARK` 会展开成一个 lambda 表达式，因此闭合大括号后必须加分号（这和最初的实验版不同）。
- `return` 是一种很方便的方式，可以避免编译器把 benchmark 代码优化掉。

直接运行这段代码就会执行 benchmark，并输出类似下面的结果：
```
-------------------------------------------------------------------------------
Fibonacci
-------------------------------------------------------------------------------
C:\path\to\Catch2\Benchmark.tests.cpp(10)
...............................................................................
benchmark name                                  samples       iterations    estimated
                                                mean          low mean      high mean
                                                std dev       low std dev   high std dev
-------------------------------------------------------------------------------
Fibonacci 20                                            100       416439   83.2878 ms
                                                       2 ns         2 ns         2 ns
                                                       0 ns         0 ns         0 ns

Fibonacci 25                                            100       400776   80.1552 ms
                                                       3 ns         3 ns         3 ns
                                                       0 ns         0 ns         0 ns

Fibonacci 30                                            100       396873   79.3746 ms
                                                      17 ns        17 ns        17 ns
                                                       0 ns         0 ns         0 ns

Fibonacci 35                                            100       145169   87.1014 ms
                                                     468 ns       464 ns       473 ns
                                                      21 ns        15 ns        34 ns
```

### 高级 benchmark
上面最简单的用法不带参数，只是运行需要测量的用户代码。
不过，如果使用 `BENCHMARK_ADVANCED` 宏，并在宏后面添加一个 `Catch::Benchmark::Chronometer` 参数，就可以使用一些高级特性。简单 benchmark 的主体会在每次 run 时执行一次，而高级 benchmark 的主体则会恰好执行两次：
一次在估算阶段，另一次在执行阶段。

```c++
BENCHMARK("simple"){ return long_computation(); };

BENCHMARK_ADVANCED("advanced")(Catch::Benchmark::Chronometer meter) {
    set_up();
    meter.measure([] { return long_computation(); });
};
```

这些高级 benchmark 不再全部由用户代码组成。在这种情况下，要被测量的代码是通过 `Catch::Benchmark::Chronometer::measure` 成员函数提供的。这让你可以在测量之外先准备好 benchmark 所需的状态，例如先构造一个随机整数向量，供排序算法使用。

一次调用 `Catch::Benchmark::Chronometer::measure` 会通过调用传入的可调用对象尽可能多次来执行实际测量。任何需要在测量之外完成的工作都可以放在 `measure` 调用之外。

传给 `measure` 的可调用对象可以选择接收一个 `int` 参数。

```c++
meter.measure([](int i) { return long_computation(i); });
```

如果它接收 `int` 参数，那么每次 run 的序号都会被传入，从 0 开始。比如当你想测量一些会修改状态的代码时，这会很有用。要预先知道 run 次数，可以调用 `Catch::Benchmark::Chronometer::runs`；这样就可以为每次 run 准备一个不同的实例供其修改。

```c++
std::vector<std::string> v(meter.runs());
std::fill(v.begin(), v.end(), test_string());
meter.measure([&v](int i) { in_place_escape(v[i]); });
```

注意，不能简单地在多次 run 中复用同一个实例，并在每次 run 后重置它，因为那样会把重置代码的开销也污染进测量结果。

简单的 `BENCHMARK` 宏也可以通过提供参数名，获得与向 `meter.measure` 提供一个接收 `int` 的 callable 相同的语义：

```c++
BENCHMARK("indexed", i){ return long_computation(i); };
```

### 构造函数和析构函数

这些工具已经很有用，但还有两类东西需要特殊处理：构造函数和析构函数。问题在于，如果你使用自动对象，它们会在作用域结束时销毁，于是你测到的是构造和析构的总时间；如果改用动态分配，又会把分配内存的时间算进去。

为了解决这个问题，Catch 提供了 class template，让你在不使用动态分配的情况下手动构造和销毁对象，并且可以分别测量构造和析构。

```c++
BENCHMARK_ADVANCED("construct")(Catch::Benchmark::Chronometer meter) {
    std::vector<Catch::Benchmark::storage_for<std::string>> storage(meter.runs());
    meter.measure([&](int i) { storage[i].construct("thing"); });
};

BENCHMARK_ADVANCED("destroy")(Catch::Benchmark::Chronometer meter) {
    std::vector<Catch::Benchmark::destructable_object<std::string>> storage(meter.runs());
    for(auto&& o : storage)
        o.construct("thing");
    meter.measure([&](int i) { storage[i].destruct(); });
};
```

`Catch::Benchmark::storage_for<T>` 只是适合存放 `T` 对象的一块原始存储。你可以使用 `Catch::Benchmark::storage_for::construct` 成员函数调用构造函数，并在这块存储里创建对象。因此，如果你想测某个构造函数运行的时间，只需要测量这个函数的执行时间即可。

当 `Catch::Benchmark::storage_for<T>` 对象的生命周期结束时，如果其中确实构造过对象，它会被自动销毁，因此不会泄漏。

如果你想测析构函数，则需要使用 `Catch::Benchmark::destructable_object<T>`。这种对象和 `Catch::Benchmark::storage_for<T>` 类似，`T` 对象的构造也是手动完成的，但它不会自动销毁任何东西。相反，你需要手动调用 `Catch::Benchmark::destructable_object::destruct` 成员函数，而这正是你可以用来测量析构时间的地方。

### 优化器

有时候优化器会把你想要测量的代码直接优化掉。通常可以用一些方式让结果变成可观察效果，例如使用 `volatile` 关键字，或者把值输出到标准输出或文件里，这两种方式都会强制程序真正生成这个值。

Catch 提供了第三种选择。由用户代码提供的函数返回值会被保证求值，不会被优化掉。这意味着如果你的用户代码只是计算某个值，你不需要再费心去用 `volatile` 或强制输出，只要直接 `return` 它即可。这样代码也能保持自然。

例如：

```c++
// may measure nothing at all by skipping the long calculation since its
// result is not used
BENCHMARK("no return"){ long_calculation(); };

// the result of long_calculation() is guaranteed to be computed somehow
BENCHMARK("with return"){ return long_calculation(); };
```

不过，除此之外并没有其他对优化器的控制手段。你需要自己写出一个真正测量到想测内容、而不是只是在测“一大堆没做事”的 benchmark。

总之，规则很简单：你在手写代码里会用来控制优化的做法，在 Catch 里也同样有效；同时，Catch 会把用户代码的返回值变成不能被优化掉的可观察效果。

<i>改编自 nonius 的文档。</i>
