import RPi.GPIO as GPIO
import time

SERVO_PIN = 18  # 使用 GPIO18（物理引脚12）

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# 设置 PWM，频率为 50Hz（舵机标准频率）
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def set_angle(angle):
    duty = 2 + (angle / 18)
    GPIO.output(SERVO_PIN, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(SERVO_PIN, False)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        set_angle(0)
        print("转到 0°")
        time.sleep(1)

        set_angle(90)
        print("转到 90°")
        time.sleep(1)

        set_angle(180)
        print("转到 180°")
        time.sleep(1)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
