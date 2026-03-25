# encoding=utf-8
from ctypes import *
from pathlib import Path
from enum import IntEnum
import os
import shutil

class BaudRate(IntEnum):
    """波特率枚举"""
    
    B2400 = 4
    B4800 = 5
    B9600 = 6
    B14400 = 7
    B19200 = 8
    B38400 = 9
    B57600 = 15
    B115200 = 16

class Parity(IntEnum):
    """校验位枚举"""
    NONE = 0x00  # 无校验
    ODD = 0x08   # 奇校验
    EVEN = 0x18  # 偶校验

class DataBits(IntEnum):
    """数据位枚举"""
    BITS_7 = 0x02
    BITS_8 = 0x03

class StopBits(IntEnum):
    """停止位枚举"""
    BITS_1 = 0x00
    BITS_2 = 0x04

class ZModemReceiver:
    """ZModem文件接收器类"""

    def __init__(self, port=9, baud_rate=BaudRate.B57600, parity=Parity.NONE, 
                 data_bits=DataBits.BITS_8, stop_bits=StopBits.BITS_1, dll_path=None,
                 receive_dir=None):
        """
        初始化ZModem接收器

        Args:
            port: 串口号，默认为9（COM9）
            baud_rate: 波特率，默认为B57600
            parity: 校验位，默认为NONE
            data_bits: 数据位，默认为BITS_8
            stop_bits: 停止位，默认为BITS_1
            dll_path: PCOMM.dll路径，默认自动查找
            receive_dir: 接收文件保存目录，默认为脚本目录下的received文件夹
        """
        self.port = port
        self.baud_rate = baud_rate
        self.parity = parity
        self.data_bits = data_bits
        self.stop_bits = stop_bits

        # 获取DLL路径
        if dll_path is None:
            base_dir = Path(__file__).resolve().parent
            self.dll_path = str(base_dir / "dll" / "x64" / "PCOMM.dll")
        else:
            self.dll_path = dll_path

        # 获取接收目录
        if receive_dir is None:
            base_dir = Path(__file__).resolve().parent
            self.receive_dir = base_dir / "received"
        else:
            self.receive_dir = Path(receive_dir)

        # 确保接收目录存在
        self.receive_dir.mkdir(parents=True, exist_ok=True)

        # 加载DLL
        self.dll = windll.LoadLibrary(self.dll_path)
        self.is_open = False

    def open(self):
        """打开串口"""
        if not self.is_open:
            try:
                self.dll.sio_open(self.port)
                # 设置串口参数
                self.dll.sio_ioctl(self.port, self.baud_rate.value, 
                                  self.parity.value | self.data_bits.value | self.stop_bits.value)
                self.is_open = True
                return True
            except Exception as e:
                print(f"打开串口失败: {e}")
                return False
        return True

    def _callback(self, recvlen, buflen, pbuf, flen):
        """接收回调函数"""
        print(recvlen, flen)
        print('\r\n')
        return 1  # 返回非0继续接收

    def receive_file(self):
        """
        接收文件

        Returns:
            tuple: (成功标志, 文件名/错误信息)
        """
        if not self.is_open:
            if not self.open():
                return False, "串口打开失败"

        try:
            # 准备回调函数
            callback_type = WINFUNCTYPE(c_int, c_long, c_int, POINTER(c_char), c_long)
            callback = callback_type(self._callback)

            # 准备文件名缓冲区
            max_path = 260
            fname = create_string_buffer(max_path)
            pfname = (POINTER(c_char) * 2)()
            pfname[0] = cast(fname, POINTER(c_char))
            pfname[1] = None

            # 开始接收
            print("等待 ZModem 接收文件...")
            ret = self.dll.sio_FtZmodemRx(self.port, pfname, 1, callback, 27)

            if ret >= 0:
                filename = fname.value.decode("gbk")
                print('ret: ', ret)
                print("接收成功！文件名：", filename)

                # 移动文件到接收目录
                try:
                    src_path = Path(filename)
                    if src_path.exists():
                        dst_path = self.receive_dir / src_path.name
                        # 如果目标文件已存在，先删除
                        if dst_path.exists():
                            dst_path.unlink()
                        shutil.move(str(src_path), str(dst_path))
                        print(f"文件已移动到: {dst_path}")
                        return True, str(dst_path)
                    else:
                        # 文件可能已经在接收目录中
                        return True, filename
                except Exception as e:
                    print(f"移动文件失败: {e}")
                    return True, filename
            else:
                print('ret: ', ret)
                print("接收失败！")
                return False, f"接收失败，错误码: {ret}"
        except Exception as e:
            print(f"接收过程出错: {e}")
            return False, str(e)

    def close(self):
        """关闭串口"""
        if self.is_open:
            try:
                self.dll.sio_close(self.port)
                self.is_open = False
                return True
            except Exception as e:
                print(f"关闭串口失败: {e}")
                return False
        return True

    def __enter__(self):
        """支持上下文管理器"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        self.close()

if __name__ == "__main__":
    # 使用示例1：直接调用（使用默认参数）
    print("=== 使用默认参数 ===")
    receiver = ZModemReceiver(port=9)
    try:
        success, result = receiver.receive_file()
        if not success:
            print(f"接收失败: {result}")
    finally:
        receiver.close()

    # 使用示例2：使用枚举参数
    print("\n=== 使用枚举参数 ===")
    receiver = ZModemReceiver(
        port=9,
        baud_rate=BaudRate.B57600,
        parity=Parity.NONE,
        data_bits=DataBits.BITS_8,
        stop_bits=StopBits.BITS_1
    )
    try:
        success, result = receiver.receive_file()
        if not success:
            print(f"接收失败: {result}")
    finally:
        receiver.close()

    # 使用示例3：上下文管理器
    # print("\n=== 使用上下文管理器 ===")
    # with ZModemReceiver(port=9) as receiver:
    #     success, result = receiver.receive_file()
    #     if not success:
    #         print(f"接收失败: {result}")
