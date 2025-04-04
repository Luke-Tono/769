#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Raspberry Pi MQ-2 Gas Sensor Test Script
Uses digital output mode to detect gas/smoke
Connected to GPIO16
'''

import RPi.GPIO as GPIO
import time

# Configuration
MQ2_PIN = 16  # GPIO16 for MQ-2 sensor digital output
LED_PIN = 20  # Optional: GPIO20 for alarm LED indicator (if you have one)
BUZZER_PIN = 21  # Optional: GPIO21 for buzzer (if you have one)

def setup():
    '''Initialize the GPIO pins'''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    # Set the MQ-2 sensor pin as input
    GPIO.setup(MQ2_PIN, GPIO.IN)
    
    # Optional: setup LED and buzzer pins as output
    # Uncomment if you have these components
    # GPIO.setup(LED_PIN, GPIO.OUT)
    # GPIO.setup(BUZZER_PIN, GPIO.OUT)
    
    print(f"MQ-2 gas sensor initialized on GPIO{MQ2_PIN}")

def callback_gas_detected(channel):
    '''Callback function to handle gas detection events'''
    if GPIO.input(MQ2_PIN):  # High means no gas/smoke detected (depends on your sensor)
        print("No gas/smoke detected")
        # Optional: turn off LED and buzzer
        # GPIO.output(LED_PIN, GPIO.LOW)
        # GPIO.output(BUZZER_PIN, GPIO.LOW)
    else:  # Low means gas/smoke detected (depends on your sensor)
        print("Gas/Smoke detected!")
        # Optional: turn on LED and buzzer
        # GPIO.output(LED_PIN, GPIO.HIGH)
        # GPIO.output(BUZZER_PIN, GPIO.HIGH)

def main():
    '''Main function'''
    try:
        setup()
        print("MQ-2 Gas Sensor Test (Press CTRL+C to exit)")
        print("Waiting for sensor to stabilize (10 seconds)...")
        time.sleep(10)  # Give the sensor some time to warm up and stabilize
        print("Sensor ready!")
        
        # Add event detection
        GPIO.add_event_detect(MQ2_PIN, GPIO.BOTH, callback=callback_gas_detected)
        
        # Initial state check
        if GPIO.input(MQ2_PIN):
            print("Initial state: No gas/smoke detected")
        else:
            print("Initial state: Gas/Smoke detected!")
        
        # Main loop to keep script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nProgram exited")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")

if __name__ == "__main__":
    main()