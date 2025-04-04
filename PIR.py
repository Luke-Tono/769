#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
树莓派PIR人体红外传感器简单测试代码
'''

import RPi.GPIO as GPIO
import time

# PIR传感器引脚定义
PIR_PIN = 17  # 使用GPIO17连接PIR传感器的输出引脚，根据实际连接修改

def setup():
    '''初始化PIR传感器'''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)  # 设置PIR引脚为输入
    print(f"PIR传感器已设置在引脚 GPIO{PIR_PIN}")
    print("等待PIR传感器初始化...")
    time.sleep(2)  # 给传感器一些启动时间
    print("PIR传感器准备就绪")

def main():
    '''主函数'''
    setup()
    print("PIR传感器测试开始（按CTRL+C退出）")
    print("当检测到运动时，将会显示消息")
    
    motion_count = 0
    last_motion_time = 0
    
    try:
        while True:
            current_time = time.time()
            
            if GPIO.input(PIR_PIN):  # 如果PIR输出高电平
                # 避免连续多次触发（至少间隔1秒）
                if current_time - last_motion_time > 1:
                    motion_count += 1
                    motion_time = time.strftime("%H:%M:%S")
                    print(f"[{motion_time}] 检测到运动！总计：{motion_count}次")
                    last_motion_time = current_time
            else:
                motion_time = time.strftime("%H:%M:%S")
                print(f"[{motion_time}] 没有运动！")
            
            time.sleep(1)  # 短暂休眠以减少CPU使用率
            
    except KeyboardInterrupt:
        print("\nPIR传感器测试已退出")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()