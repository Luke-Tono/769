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

def setup():
    '''Initialize the GPIO pins'''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    # Set the MQ-2 sensor pin as input
    GPIO.setup(MQ2_PIN, GPIO.IN)
    
    print(f"MQ-2 gas sensor initialized on GPIO{MQ2_PIN}")

def main():
    '''Main function'''
    try:
        setup()
        print("MQ-2 Gas Sensor Test (Press CTRL+C to exit)")
        print("Waiting for sensor to stabilize (10 seconds)...")
        time.sleep(10)  # Give the sensor some time to warm up and stabilize
        print("Sensor ready!")
        
        # Initial state check
        last_state = GPIO.input(MQ2_PIN)
        if last_state:
            print("Initial state: No gas/smoke detected")
        else:
            print("Initial state: Gas/Smoke detected!")
        
        # Main loop to continuously check sensor
        while True:
            current_state = GPIO.input(MQ2_PIN)
            
            # Only print when state changes
            if current_state != last_state:
                if current_state:
                    print("No gas/smoke detected")
                else:
                    print("Gas/Smoke detected!")
                
                last_state = current_state
            
            time.sleep(0.5)  # Check every 0.5 seconds
            
    except KeyboardInterrupt:
        print("\nProgram exited")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")

if __name__ == "__main__":
    main()
