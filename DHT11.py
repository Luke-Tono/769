import RPi.GPIO as GPIO
import dht11
import time

# 设置 GPIO 模式
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# 初始化 DHT11，假设你接在 GPIO 4
instance = dht11.DHT11(pin=4)

while True:
    result = instance.read()
    if result.is_valid():
        print(f"温度: {result.temperature}°C, 湿度: {result.humidity}%")
    else:
        print("读取失败")
    time.sleep(0.5)
