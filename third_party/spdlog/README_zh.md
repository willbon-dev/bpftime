# spdlog

 
[![ci](https://github.com/gabime/spdlog/actions/workflows/linux.yml/badge.svg)](https://github.com/gabime/spdlog/actions/workflows/linux.yml)&nbsp;
[![ci](https://github.com/gabime/spdlog/actions/workflows/windows.yml/badge.svg)](https://github.com/gabime/spdlog/actions/workflows/windows.yml)&nbsp;
[![ci](https://github.com/gabime/spdlog/actions/workflows/macos.yml/badge.svg)](https://github.com/gabime/spdlog/actions/workflows/macos.yml)&nbsp;
[![Build status](https://ci.appveyor.com/api/projects/status/d2jnxclg20vd0o50?svg=true&branch=v1.x)](https://ci.appveyor.com/project/gabime/spdlog) [![Release](https://img.shields.io/github/release/gabime/spdlog.svg)](https://github.com/gabime/spdlog/releases/latest)

快速的 C++ 日志库

## 安装
#### 头文件版
把 include [目录](https://github.com/gabime/spdlog/tree/v1.x/include/spdlog) 复制到你的构建树中，并使用支持 C++11 的编译器。

#### 编译版（推荐 - 编译速度快很多）
```console
$ git clone https://github.com/gabime/spdlog.git
$ cd spdlog && mkdir build && cd build
$ cmake .. && cmake --build .
```
如何使用请参考示例 [CMakeLists.txt](https://github.com/gabime/spdlog/blob/v1.x/example/CMakeLists.txt)。

## 平台
* Linux、FreeBSD、OpenBSD、Solaris、AIX
* Windows（msvc 2013+、cygwin）
* macOS（clang 3.5+）
* Android

## 包管理器：
* Debian: `sudo apt install libspdlog-dev`
* Homebrew: `brew install spdlog`
* MacPorts: `sudo port install spdlog`
* FreeBSD:  `pkg install spdlog`
* Fedora: `dnf install spdlog`
* Gentoo: `emerge dev-libs/spdlog`
* Arch Linux: `pacman -S spdlog`
* openSUSE: `sudo zypper in spdlog-devel`
* ALT Linux: `apt-get install libspdlog-devel`
* vcpkg: `vcpkg install spdlog`
* conan: `conan install --requires=spdlog/[*]`
* conda: `conda install -c conda-forge spdlog`
* build2: ```depends: spdlog ^1.8.2```

## 特性
* 非常快（见下面的 [benchmarks](#benchmarks)）。
* 仅头文件或编译版都可用
* 功能丰富的格式化，使用优秀的 [fmt](https://github.com/fmtlib/fmt) 库。
* 异步模式（可选）
* [自定义](https://github.com/gabime/spdlog/wiki/3.-Custom-formatting) 格式化。
* 支持多线程/单线程 logger。
* 各种日志目标：
  * 轮转日志文件。
  * 每日日志文件。
  * 控制台日志（支持颜色）。
  * syslog。
  * Windows event log。
  * Windows debugger（```OutputDebugString(..)```）。
  * 写入 Qt widget（见 [示例](#log-to-qt-with-nice-colors)）。
  * 很容易通过自定义日志目标进行[扩展](https://github.com/gabime/spdlog/wiki/4.-Sinks#implementing-your-own-sink)。
* 日志过滤 - 日志级别既可以在运行时修改，也可以在编译期修改。
* 支持从 argv 或环境变量加载日志级别。
* [Backtrace](#backtrace-support) 支持 - 把调试消息存入环形缓冲区，并在需要时再显示。

## 使用示例

#### 基本用法
```c++
#include "spdlog/spdlog.h"

int main() 
{
    spdlog::info("Welcome to spdlog!");
    spdlog::error("Some error message with arg: {}", 1);
    
    spdlog::warn("Easy padding in numbers like {:08d}", 12);
    spdlog::critical("Support for int: {0:d};  hex: {0:x};  oct: {0:o}; bin: {0:b}", 42);
    spdlog::info("Support for floats {:03.2f}", 1.23456);
    spdlog::info("Positional args are {1} {0}..", "too", "supported");
    spdlog::info("{:<30}", "left aligned");
    
    spdlog::set_level(spdlog::level::debug); // 将全局日志级别设为 debug
    spdlog::debug("This message should be displayed..");    
    
    // change log pattern
    spdlog::set_pattern("[%H:%M:%S %z] [%n] [%^---%L---%$] [thread %t] %v");
    
    // 编译期日志级别
    // 注意，这不会改变当前日志级别，它只会在发布代码中根据
    // SPDLOG_ACTIVE_LEVEL 移除对应调用。
    SPDLOG_TRACE("Some trace message with param {}", 42);
    SPDLOG_DEBUG("Some debug message");
}

```
---
#### 创建 stdout/stderr logger 对象
```c++
#include "spdlog/spdlog.h"
#include "spdlog/sinks/stdout_color_sinks.h"
void stdout_example()
{
    // create a color multi-threaded logger
    auto console = spdlog::stdout_color_mt("console");    
    auto err_logger = spdlog::stderr_color_mt("stderr");    
    spdlog::get("console")->info("loggers can be retrieved from a global registry using the spdlog::get(logger_name)");
}
```

---
#### 基本文件 logger
```c++
#include "spdlog/sinks/basic_file_sink.h"
void basic_logfile_example()
{
    try 
    {
        auto logger = spdlog::basic_logger_mt("basic_logger", "logs/basic-log.txt");
    }
    catch (const spdlog::spdlog_ex &ex)
    {
        std::cout << "Log init failed: " << ex.what() << std::endl;
    }
}
```
---
#### 轮转文件
```c++
#include "spdlog/sinks/rotating_file_sink.h"
void rotating_example()
{
    // 创建一个文件轮转 logger，最大 5 MB，保留 3 个轮转文件
    auto max_size = 1048576 * 5;
    auto max_files = 3;
    auto logger = spdlog::rotating_logger_mt("some_logger_name", "logs/rotating.txt", max_size, max_files);
}
```

---
#### 每日文件
```c++

#include "spdlog/sinks/daily_file_sink.h"
void daily_example()
{
    // 创建一个每日 logger - 每天凌晨 2:30 会生成一个新文件
    auto logger = spdlog::daily_logger_mt("daily_logger", "logs/daily.txt", 2, 30);
}

```

---
#### Backtrace 支持
```c++
// 调试消息可以存入环形缓冲区，而不是立即记录。
// 这对于只在需要时显示调试日志很有用（例如发生错误时）。
// 需要时，调用 dump_backtrace() 把它们输出到日志中。

spdlog::enable_backtrace(32); // 把最近 32 条消息存入缓冲区。
// 或 my_logger->enable_backtrace(32)..
for(int i = 0; i < 100; i++)
{
  spdlog::debug("Backtrace message {}", i); // 还不会立即记录
}
// 例如，如果发生了错误：
spdlog::dump_backtrace(); // 现在把它们记录下来！输出最近 32 条消息
// 或 my_logger->dump_backtrace(32)..
```

---
#### 定期 flush
```c++
// 每 3 秒定期 flush 所有*已注册* logger：
// 警告：只有当所有 logger 都是线程安全的（"_mt" logger）时才使用
spdlog::flush_every(std::chrono::seconds(3));

```

---
#### Stopwatch
```c++
// spdlog 的 stopwatch 支持
#include "spdlog/stopwatch.h"
void stopwatch_example()
{
    spdlog::stopwatch sw;    
    spdlog::debug("Elapsed {}", sw);
    spdlog::debug("Elapsed {:.3}", sw);       
}

```

---
#### 以十六进制日志化二进制数据
```c++
// 许多 std::container<char> 类型都可以使用。
// 也支持 ranges。
// 格式标志：
// {:X} - 大写输出。
// {:s} - 不在每个字节之间加空格。
// {:p} - 不在每行开头打印位置。
// {:n} - 不把输出分成多行。
// {:a} - 如果没设置 :n，则显示 ASCII。

#include "spdlog/fmt/bin_to_hex.h"

void binary_example()
{
    auto console = spdlog::get("console");
    std::array<char, 80> buf;
    console->info("Binary example: {}", spdlog::to_hex(buf));
    console->info("Another binary example:{:n}", spdlog::to_hex(std::begin(buf), std::begin(buf) + 10));
    // 更多示例：
    // logger->info("uppercase: {:X}", spdlog::to_hex(buf));
    // logger->info("uppercase, no delimiters: {:Xs}", spdlog::to_hex(buf));
    // logger->info("uppercase, no delimiters, no position info: {:Xsp}", spdlog::to_hex(buf));
}

```

---
#### 一个 logger 配多个 sink - 每个 sink 使用不同的格式和日志级别
```c++

// 创建一个带 2 个目标的 logger，不同目标使用不同的日志级别和格式。
// 控制台只显示警告或错误，而文件会记录全部内容。
void multi_sink_example()
{
    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    console_sink->set_level(spdlog::level::warn);
    console_sink->set_pattern("[multi_sink_example] [%^%l%$] %v");

    auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>("logs/multisink.txt", true);
    file_sink->set_level(spdlog::level::trace);

    spdlog::logger logger("multi_sink", {console_sink, file_sink});
    logger.set_level(spdlog::level::debug);
    logger.warn("this should appear in both console and file");
    logger.info("this message should not appear in the console, only in the file");
}
```

---
#### 关于日志事件的用户自定义回调
```c++

// 创建一个带 lambda 回调的 logger；每次向该 logger 记录内容时都会调用回调
void callback_example()
{
    auto callback_sink = std::make_shared<spdlog::sinks::callback_sink_mt>([](const spdlog::details::log_msg &msg) {
         // 例如，你可以通过发邮件通知自己
    });
    callback_sink->set_level(spdlog::level::err);

    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    spdlog::logger logger("custom_callback_logger", {console_sink, callback_sink});

    logger.info("some info log");
    logger.error("critical issue"); // 会通知你
}
```

---
#### 异步日志
```c++
#include "spdlog/async.h"
#include "spdlog/sinks/basic_file_sink.h"
void async_example()
{
    // 默认线程池设置可以在创建 async logger 之前修改：
    // spdlog::init_thread_pool(8192, 1); // 8k 队列，1 个后台线程。
    auto async_file = spdlog::basic_logger_mt<spdlog::async_factory>("async_file_logger", "logs/async_log.txt");
    // 或者：
    // auto async_file = spdlog::create_async<spdlog::sinks::basic_file_sink_mt>("async_file_logger", "logs/async_log.txt");   
}

```

---
#### 带多 sink 的异步 logger
```c++
#include "spdlog/async.h"
#include "spdlog/sinks/stdout_color_sinks.h"
#include "spdlog/sinks/rotating_file_sink.h"

void multi_sink_example2()
{
    spdlog::init_thread_pool(8192, 1);
    auto stdout_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt >();
    auto rotating_sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>("mylog.txt", 1024*1024*10, 3);
    std::vector<spdlog::sink_ptr> sinks {stdout_sink, rotating_sink};
    auto logger = std::make_shared<spdlog::async_logger>("loggername", sinks.begin(), sinks.end(), spdlog::thread_pool(), spdlog::async_overflow_policy::block);
    spdlog::register_logger(logger);
}
```
 
---
#### 用户自定义类型
```c++
template<>
struct fmt::formatter<my_type> : fmt::formatter<std::string>
{
    auto format(my_type my, format_context &ctx) const -> decltype(ctx.out())
    {
        return fmt::format_to(ctx.out(), "[my_type i={}]", my.i);
    }
};

void user_defined_example()
{
    spdlog::info("user defined type: {}", my_type(14));
}

```

---
#### 日志 pattern 中的用户自定义 flag
```c++ 
// 日志 pattern 可以包含自定义 flag。
// 下面的示例会添加新的 flag '%*'，它会绑定到 <my_formatter_flag> 实例。
#include "spdlog/pattern_formatter.h"
class my_formatter_flag : public spdlog::custom_flag_formatter
{
public:
    void format(const spdlog::details::log_msg &, const std::tm &, spdlog::memory_buf_t &dest) override
    {
        std::string some_txt = "custom-flag";
        dest.append(some_txt.data(), some_txt.data() + some_txt.size());
    }

    std::unique_ptr<custom_flag_formatter> clone() const override
    {
        return spdlog::details::make_unique<my_formatter_flag>();
    }
};

void custom_flags_example()
{    
    auto formatter = std::make_unique<spdlog::pattern_formatter>();
    formatter->add_flag<my_formatter_flag>('*').set_pattern("[%n] [%*] [%^%l%$] %v");
    spdlog::set_formatter(std::move(formatter));
}

```

---
#### 自定义错误处理器
```c++
void err_handler_example()
{
    // 可以全局设置，也可以按 logger 设置（logger->set_error_handler(..)）
    spdlog::set_error_handler([](const std::string &msg) { spdlog::get("console")->error("*** LOGGER ERROR ***: {}", msg); });
    spdlog::get("console")->info("some invalid message to trigger an error {}{}{}{}", 3);
}

```

---
#### syslog
```c++
#include "spdlog/sinks/syslog_sink.h"
void syslog_example()
{
    std::string ident = "spdlog-example";
    auto syslog_logger = spdlog::syslog_logger_mt("syslog", ident, LOG_PID);
    syslog_logger->warn("This is warning that will end up in syslog.");
}
```
---
#### Android 示例
```c++
#include "spdlog/sinks/android_sink.h"
void android_example()
{
    std::string tag = "spdlog-android";
    auto android_logger = spdlog::android_logger_mt("android", tag);
    android_logger->critical("Use \"adb shell logcat\" to view this message.");
}
```

---
#### 从环境变量或 argv 加载日志级别

```c++
#include "spdlog/cfg/env.h"
int main (int argc, char *argv[])
{
    spdlog::cfg::load_env_levels();
    // 或者指定环境变量名：
    // MYAPP_LEVEL=info,mylogger=trace && ./example
    // spdlog::cfg::load_env_levels("MYAPP_LEVEL");
    // 或者从命令行加载：
    // ./example SPDLOG_LEVEL=info,mylogger=trace
    // #include "spdlog/cfg/argv.h" // 从 argv 加载级别时使用
    // spdlog::cfg::load_argv_levels(argc, argv);
}
```
然后你可以这样用：

```console
$ export SPDLOG_LEVEL=info,mylogger=trace
$ ./example
```


---
#### 日志文件打开/关闭事件处理器
```c++
// 你可以在日志文件打开或关闭前后收到 spdlog 的回调。
// 这对于清理流程或者在日志文件开头/结尾写入内容都很有用。
void file_events_example()
{
    // 将 spdlog::file_event_handlers 传给 file sink，以便接收打开/关闭日志文件通知
    spdlog::file_event_handlers handlers;
    handlers.before_open = [](spdlog::filename_t filename) { spdlog::info("Before opening {}", filename); };
    handlers.after_open = [](spdlog::filename_t filename, std::FILE *fstream) { fputs("After opening\n", fstream); };
    handlers.before_close = [](spdlog::filename_t filename, std::FILE *fstream) { fputs("Before closing\n", fstream); };
    handlers.after_close = [](spdlog::filename_t filename) { spdlog::info("After closing {}", filename); };
    auto my_logger = spdlog::basic_logger_st("some_logger", "logs/events-sample.txt", true, handlers);        
}
```

---
#### 替换默认 logger
```c++
void replace_default_logger_example()
{
    auto new_logger = spdlog::basic_logger_mt("new_default_logger", "logs/new-default-log.txt", true);
    spdlog::set_default_logger(new_logger);
    spdlog::info("new logger log message");
}
```

---
#### 用更漂亮的颜色写入 Qt
```c++
#include "spdlog/spdlog.h"
#include "spdlog/sinks/qt_sinks.h"
MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent)
{
    setMinimumSize(640, 480);
    auto log_widget = new QTextEdit(this);
    setCentralWidget(log_widget);
    int max_lines = 500; // 将文本控件限制为最多 500 行，必要时删除旧行。
    auto logger = spdlog::qt_color_logger_mt("qt_logger", log_widget, max_lines);
    logger->info("Some info message");
}
```
---

#### Mapped Diagnostic Context
```c++
// Mapped Diagnostic Context (MDC) 是一个在线程局部存储中保存键值对（字符串值）的 map。
// 每个线程维护自己的 MDC，logger 会用它把诊断信息附加到日志输出中。
// 注意：由于它依赖线程局部存储，因此在异步模式下不受支持。
#include "spdlog/mdc.h"
void mdc_example()
{
    spdlog::mdc::put("key1", "value1");
    spdlog::mdc::put("key2", "value2");
    // 如果不用默认格式，可以用 %& formatter 来打印 mdc 数据
    // spdlog::set_pattern("[%H:%M:%S %z] [%^%L%$] [%&] %v");
}
```
---
## Benchmarks

下面这些 [benchmarks](https://github.com/gabime/spdlog/blob/v1.x/bench/bench.cpp) 是在 Ubuntu 64 bit、Intel i7-4770 CPU @ 3.40GHz 上测得的。

#### 同步模式
```
[info] **************************************************************
[info] Single thread, 1,000,000 iterations
[info] **************************************************************
[info] basic_st         Elapsed: 0.17 secs        5,777,626/sec
[info] rotating_st      Elapsed: 0.18 secs        5,475,894/sec
[info] daily_st         Elapsed: 0.20 secs        5,062,659/sec
[info] empty_logger     Elapsed: 0.07 secs       14,127,300/sec
[info] **************************************************************
[info] C-string (400 bytes). Single thread, 1,000,000 iterations
[info] **************************************************************
[info] basic_st         Elapsed: 0.41 secs        2,412,483/sec
[info] rotating_st      Elapsed: 0.72 secs        1,389,196/sec
[info] daily_st         Elapsed: 0.42 secs        2,393,298/sec
[info] null_st          Elapsed: 0.04 secs       27,446,957/sec
[info] **************************************************************
[info] 10 threads, competing over the same logger object, 1,000,000 iterations
[info] **************************************************************
[info] basic_mt         Elapsed: 0.60 secs        1,659,613/sec
[info] rotating_mt      Elapsed: 0.62 secs        1,612,493/sec
[info] daily_mt         Elapsed: 0.61 secs        1,638,305/sec
[info] null_mt          Elapsed: 0.16 secs        6,272,758/sec
```
#### 异步模式
```
[info] -------------------------------------------------
[info] Messages     : 1,000,000
[info] Threads      : 10
[info] Queue        : 8,192 slots
[info] Queue memory : 8,192 x 272 = 2,176 KB 
[info] -------------------------------------------------
[info] 
[info] *********************************
[info] Queue Overflow Policy: block
[info] *********************************
[info] Elapsed: 1.70784 secs     585,535/sec
[info] Elapsed: 1.69805 secs     588,910/sec
[info] Elapsed: 1.7026 secs      587,337/sec
[info] 
[info] *********************************
[info] Queue Overflow Policy: overrun
[info] *********************************
[info] Elapsed: 0.372816 secs    2,682,285/sec
[info] Elapsed: 0.379758 secs    2,633,255/sec
[info] Elapsed: 0.373532 secs    2,677,147/sec

```

## 文档
文档可以在 [wiki](https://github.com/gabime/spdlog/wiki/1.-QuickStart) 页面找到。

---

感谢 [JetBrains](https://www.jetbrains.com/?from=spdlog) 捐赠产品许可证，帮助开发 **spdlog** <a href="https://www.jetbrains.com/?from=spdlog"><img src="logos/jetbrains-variant-4.svg" width="94" align="center" /></a>


