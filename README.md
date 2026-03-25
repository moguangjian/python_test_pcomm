# python\_test\_pcomm

在win10 64wug中文版中，使用python3调用pcomm lite 1.9的动态库使用zmodem协议进行文件传输的代码示例

Code example for using Python3 to call the dynamic library of Pcomm Lite 1.9 for file transfer via the Zmodem protocol on Windows 10 64bits Chinese edition.

## 项目简介

本项目提供了使用 Python 3 调用 Pcomm Lite 1.9 动态库，通过 Zmodem 协议进行文件传输的示例代码。主要包括：

- `test_rec.py`：接收文件的示例代码
- `test_send.py`：发送文件的示例代码

## 环境要求

- Windows 10 中文版
- Python 3.7+
- Pcomm Lite 1.9 动态库

## 安装步骤

1. 克隆本项目到本地
2. 确保 Pcomm Lite 1.9 动态库已正确安装，并且 `dll/x64/PCOMM.dll` 文件存在
3. 安装 Python 依赖（如果需要）

## 使用方法

### 接收文件

```python
from test_rec import ZModemReceiver

# 使用默认参数
receiver = ZModemReceiver(port=9)
try:
    success, result = receiver.receive_file()
    if not success:
        print(f"接收失败: {result}")
finally:
    receiver.close()

# 使用自定义接收目录
receiver = ZModemReceiver(port=9, receive_dir="D:/custom_received")
try:
    success, result = receiver.receive_file()
    if not success:
        print(f"接收失败: {result}")
finally:
    receiver.close()

# 使用上下文管理器
with ZModemReceiver(port=9) as receiver:
    success, result = receiver.receive_file()
    if not success:
        print(f"接收失败: {result}")
```

### 发送文件

```python
from test_send import ZModemSender

# 使用默认参数
sender = ZModemSender(port=8)
try:
    success, result = sender.send_file('d:\\test.txt')
    if not success:
        print(f"发送失败: {result}")
finally:
    sender.close()

# 使用上下文管理器
with ZModemSender(port=8) as sender:
    success, result = sender.send_file('d:\\test.txt')
    if not success:
        print(f"发送失败: {result}")
```

## 代码结构

- `test_rec.py`：ZModem 接收文件的实现
  - `ZModemReceiver` 类：处理文件接收逻辑
  - 支持自定义接收目录
  - 支持上下文管理器
- `test_send.py`：ZModem 发送文件的实现
  - `ZModemSender` 类：处理文件发送逻辑
  - 支持上下文管理器
- `dll/`：Pcomm Lite 动态库
  - `x64/`：64位动态库
  - `x86/`：32位动态库
- `received/`：接收文件的默认保存目录
- `resource/`：Pcomm Lite 相关资源文件

## 串口参数

项目中使用的串口参数枚举：

- `BaudRate`：波特率枚举（2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200）
- `Parity`：校验位枚举（NONE, ODD, EVEN）
- `DataBits`：数据位枚举（BITS\_7, BITS\_8）
- `StopBits`：停止位枚举（BITS\_1, BITS\_2）

## 注意事项

1. 确保串口连接正确
2. 确保 Pcomm Lite 动态库路径正确
3. 接收文件时，确保目标目录有写权限
4. 发送文件时，确保源文件存在

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
