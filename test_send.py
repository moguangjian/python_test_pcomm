# encoding=utf-8
from ctypes import *
from pathlib import Path
from enum import IntEnum


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


class ZModemSender:
    """ZModem文件发送器类"""
    
    def __init__(self, port=8, baud_rate=BaudRate.B57600, parity=Parity.NONE, 
                 data_bits=DataBits.BITS_8, stop_bits=StopBits.BITS_1, dll_path=None):
        """
        初始化ZModem发送器
        
        Args:
            port: 串口号，默认为8（COM8）
            baud_rate: 波特率，默认为B57600
            parity: 校验位，默认为NONE
            data_bits: 数据位，默认为BITS_8
            stop_bits: 停止位，默认为BITS_1
            dll_path: PCOMM.dll路径，默认自动查找
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
    
    def _callback(self, xmitlen, buflen, pbuf, flen):
        """发送回调函数"""
        print(xmitlen, flen)
        print('\r\n')
        return xmitlen
    
    def send_file(self, file_path):
        """
        发送文件
        
        Args:
            file_path: 要发送的文件路径
            
        Returns:
            tuple: (成功标志, 错误信息)
        """
        if not self.is_open:
            if not self.open():
                return False, "串口打开失败"
        
        try:
            # 准备回调函数
            callback_type = WINFUNCTYPE(c_int, c_long, c_int, POINTER(c_char), c_long)
            callback = callback_type(self._callback)
            
            # 开始发送
            print(f"开始发送文件: {file_path}")
            ret = self.dll.sio_FtZmodemTx(self.port, file_path.encode('ascii'), callback, 27)
            
            print('ret: ', ret)
            if ret >= 0:
                print("发送成功！")
                return True, "发送成功"
            else:
                print("发送失败！")
                return False, f"发送失败，错误码: {ret}"
        except Exception as e:
            print(f"发送过程出错: {e}")
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
    sender = ZModemSender(port=8)
    try:
        success, result = sender.send_file('d:\\test.txt')
        if not success:
            print(f"发送失败: {result}")
    finally:
        sender.close()
    
    # 使用示例2：使用枚举参数
    print("\n=== 使用枚举参数 ===")
    sender = ZModemSender(
        port=8,
        baud_rate=BaudRate.B57600,
        parity=Parity.NONE,
        data_bits=DataBits.BITS_8,
        stop_bits=StopBits.BITS_1
    )
    try:
        success, result = sender.send_file(r'.\test.txt')
        if not success:
            print(f"发送失败: {result}")
    finally:
        sender.close()
    
    # 使用示例3：上下文管理器
    # print("\n=== 使用上下文管理器 ===")
    # with ZModemSender(port=8) as sender:
    #     success, result = sender.send_file('d:\\test.txt')
    #     if not success:
    #         print(f"发送失败: {result}")