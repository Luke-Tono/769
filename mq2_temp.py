#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time

MQ2_PIN = 16  # GPIO16

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MQ2_PIN, GPIO.IN)
    print(f"MQ-2 gas sensor initialized on GPIO{MQ2_PIN}")

def main():
    try:
        setup()
        print("MQ-2 Gas Sensor Test (Press CTRL+C to exit)")
        print("Waiting for sensor to stabilize (10 seconds)...")
        time.sleep(10)
        print("Sensor ready!")

        while True:
            state = GPIO.input(MQ2_PIN)
            if state:
                print("No gas/smoke detected")
            else:
                print("Gas/Smoke detected!")
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\nProgram exited by user.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")

if __name__ == "__main__":
    main()
