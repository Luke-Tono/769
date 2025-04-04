#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Raspberry Pi Integrated Sensor System with PubNub Integration
Combines the following functions:
1. Temperature/humidity sensor (DHT11) reading and display on LCD 1602A
2. PIR motion detection
3. Servo motor control for air vent
4. MQ-2 gas/smoke sensor detection
5. Real-time data publishing to PubNub cloud

Author: Integrated from original separate files
Date: 2025-04-04
'''

import RPi.GPIO as GPIO
import time
import dht11
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException
import json

# ===== PUBNUB CONFIGURATION =====
pnconfig = PNConfiguration()
pnconfig.publish_key = "pub-c-cc09a5e0-ae7e-4f0b-91ba-3c06deac8056"
pnconfig.subscribe_key = "sub-c-600de055-e08b-4dfd-8f69-231ee45b2313"
pnconfig.uuid = "z728"
pubnub = PubNub(pnconfig)
CHANNEL = "zhaox207"

# ===== PIN CONFIGURATION =====
# DHT11 temperature and humidity sensor
DHT_PIN = 4  # GPIO4

# LCD 1602A display
LCD_RS = 26  # GPIO26
LCD_E = 19   # GPIO19
LCD_D4 = 13  # GPIO13
LCD_D5 = 6   # GPIO6
LCD_D6 = 5   # GPIO5
LCD_D7 = 11  # GPIO11

# PIR motion sensor
PIR_PIN = 17  # GPIO17

# Servo motor
SERVO_PIN = 18  # GPIO18

# MQ-2 gas sensor
MQ2_PIN = 16  # GPIO16

# ===== LCD DISPLAY CONSTANTS =====
LCD_WIDTH = 16    # LCD character width
LCD_LINE_1 = 0x80 # LCD RAM address for 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for 3rd line (if available)
LCD_LINE_4 = 0xD4 # LCD RAM address for 4th line (if available)
LCD_CHR = True    # Send data
LCD_CMD = False   # Send command
E_PULSE = 0.0005  # E pulse width
E_DELAY = 0.0005  # E delay

# LCD DISPLAY FUNCTIONS (Unchanged from previous script)
# ... [Keep the existing lcd_init(), lcd_byte(), lcd_toggle_enable(), lcd_string(), lcd_clear() functions] ...

# ===== SERVO CONTROL FUNCTIONS (Unchanged) =====
# ... [Keep the existing servo_init() and set_angle() functions] ...

# ===== PIR MOTION SENSOR FUNCTIONS (Unchanged) =====
# ... [Keep the existing pir_init() and check_motion() functions] ...

# ===== MQ-2 GAS SENSOR FUNCTIONS =====
def mq2_init():
    '''Initialize MQ-2 gas sensor'''
    GPIO.setup(MQ2_PIN, GPIO.IN)
    print(f"MQ-2 gas sensor initialized on GPIO{MQ2_PIN}")
    
    # Wait for sensor to stabilize
    print("Waiting for MQ-2 sensor to stabilize...")
    time.sleep(10)
    print("MQ-2 sensor ready")

def check_gas():
    '''Check if gas/smoke is detected'''
    # Note: Depends on sensor's output logic. 
    # Some sensors return LOW when gas is detected, some return HIGH
    # Modify according to your specific sensor's behavior
    return GPIO.input(MQ2_PIN) == 0  # Assumes LOW means gas detected

# ===== PUBNUB FUNCTIONS =====
def publish_to_pubnub(temp, humidity, motion, gas_detected):
    '''Publish sensor data to PubNub'''
    try:
        message = {
            "temperature": temp,
            "humidity": humidity,
            "motion": motion,
            "gas_detected": gas_detected
        }
        
        envelope = pubnub.publish().channel(CHANNEL).message(message).sync()
        if envelope.status.is_error():
            print(f"[PubNub] Error: {envelope.status.error}")
        else:
            print(f"[PubNub] Message published successfully")
    except PubNubException as e:
        print(f"[PubNub] Exception: {e}")
    except Exception as e:
        print(f"[PubNub] Unexpected error: {e}")

# ===== SMART CONTROL LOGIC =====
def decide_vent_position(temp, humidity, motion_detected, gas_detected, last_motion_time, current_time):
    '''Decide vent position based on sensor data'''
    # Configuration parameters
    TEMP_HIGH = 26  # High temperature threshold (Celsius)
    TEMP_LOW = 18   # Low temperature threshold (Celsius)
    HUMIDITY_HIGH = 70  # High humidity threshold (percentage)
    NO_MOTION_CLOSE_TIME = 300  # Time to close vent after no motion (seconds)
    
    # Default position: half open (90 degrees)
    position = 90
    reason = "Normal ventilation"
    
    # High priority: Gas detection
    if gas_detected:
        position = 180  # Fully open for ventilation
        reason = "Gas/Smoke Detected"
        return position, reason
    
    # Adjust based on temperature
    if temp > TEMP_HIGH:
        position = 180  # High temp, fully open
        reason = f"High temp ({temp}C)"
    elif temp < TEMP_LOW:
        position = 0  # Low temp, closed
        reason = f"Low temp ({temp}C)"
    
    # Adjust based on humidity (only when temperature is in normal range)
    if TEMP_LOW <= temp <= TEMP_HIGH and humidity > HUMIDITY_HIGH:
        position = 180  # High humidity, fully open
        reason = f"High humidity ({humidity}%)"
    
    # Adjust based on motion detection
    no_motion_time = current_time - last_motion_time
    if not motion_detected and no_motion_time > NO_MOTION_CLOSE_TIME:
        # Long time no motion, close vent to save energy
        position = 0
        reason = f"No motion ({int(no_motion_time//60)}min)"
    
    return position, reason

# ===== MAIN PROGRAM =====
def main():
    try:
        # Set GPIO mode
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()  # Clean up previous settings
        
        # Initialize LCD
        lcd_init()
        print("LCD screen initialized")
        
        # Initialize DHT11
        dht_sensor = dht11.DHT11(pin=DHT_PIN)
        print("DHT11 temperature/humidity sensor initialized")
        
        # Initialize servo
        servo_init()
        
        # Initialize PIR sensor
        pir_init()
        
        # Initialize MQ-2 gas sensor
        mq2_init()
        
        # Display welcome message
        lcd_string("Smart Air Vent", LCD_LINE_1)
        lcd_string("Initializing...", LCD_LINE_2)
        time.sleep(2)
        
        motion_count = 0
        last_motion_time = time.time()  # Initialize to current time
        error_count = 0
        servo_position = 90  # Initial servo position (half open)
        set_angle(servo_position)  # Set initial position
        last_detected_motion = False  # Last motion state
        last_detected_gas = False  # Last gas detection state
        display_toggle_time = time.time()  # Last display toggle time
        last_vent_change_time = 0  # Last vent position change time
        current_reason = "Initial state"  # Current reason for vent position
        last_pubnub_time = 0  # Last time data was published to PubNub
        
        print("System startup complete, monitoring...")
        
        while True:
            current_time = time.time()
            time_str = time.strftime("%H:%M:%S")
            
            # 1. Read DHT11 temperature/humidity data
            result = dht_sensor.read()
            current_second = int(time.strftime("%S"))
            display_mode = (current_second // 5) % 4  # Cycle display mode every 5 seconds 
            
            if result.is_valid():
                temp = result.temperature
                humidity = result.humidity
                
                # Detect current motion state
                current_motion = check_motion()
                if current_motion and not last_detected_motion:
                    if current_time - last_motion_time > 1:  # Avoid consecutive triggers
                        motion_count += 1
                        print(f"[{time_str}] Motion detected! Total: {motion_count}")
                        last_motion_time = current_time
                
                # Detect current gas state
                current_gas = check_gas()
                if current_gas and not last_detected_gas:
                    print(f"[{time_str}] Gas/Smoke detected!")
                
                # Update detection states
                last_detected_motion = current_motion
                last_detected_gas = current_gas
                
                # Decide vent position
                if current_time - last_vent_change_time > 10:  # Adjust vent position at most once every 10 seconds
                    new_position, reason = decide_vent_position(
                        temp, humidity, current_motion, current_gas, 
                        last_motion_time, current_time
                    )
                    
                    # If position needs to change, control servo
                    if new_position != servo_position:
                        print(f"[{time_str}] Adjusting vent: {servo_position}° -> {new_position}° (Reason: {reason})")
                        servo_position = new_position
                        set_angle(servo_position)
                        current_reason = reason
                        last_vent_change_time = current_time
                
                # Decide what to display based on display mode
                if display_mode == 0:  # Display temperature/humidity
                    temp_str = f"Temp: {temp}C"
                    hum_str = f"Hum: {humidity}% {time_str[-5:]}"
                    
                    lcd_string(temp_str, LCD_LINE_1)
                    lcd_string(hum_str, LCD_LINE_2)
                elif display_mode == 1:  # Display PIR data
                    lcd_string("Motion Detector", LCD_LINE_1)
                    status = "ACTIVE" if current_motion else "Inactive"
                    lcd_string(f"Status: {status}", LCD_LINE_2)
                elif display_mode == 2:  # Display vent status
                    vent_status = "Off" if servo_position == 0 else "On"
                    if 0 < servo_position < 180:
                        vent_status = f"{int(servo_position/180*100)}%"
                    
                    lcd_string(f"Vent: {vent_status}", LCD_LINE_1)
                    lcd_string(f"Reason: {current_reason[:16]}", LCD_LINE_2)  # Limit to 16 characters
                else:  # Display gas/smoke status
                    gas_status = "GAS ALERT!" if current_gas else "Gas: Normal"
                    lcd_string("Gas/Smoke Sensor", LCD_LINE_1)
                    lcd_string(gas_status, LCD_LINE_2)
                
                print(f"[{time_str}] Temp: {temp}°C, Humidity: {humidity}%, Vent: {servo_position}°, Gas: {current_gas}")
                error_count = 0
                
                # Publish data to PubNub every 5 seconds
                if current_time - last_pubnub_time > 5:
                    publish_to_pubnub(temp, humidity, current_motion, current_gas)
                    last_pubnub_time = current_time
                    
            else:
                error_count += 1
                print(f"[{time_str}] Sensor read failed, attempt: {error_count}")
                
                if error_count > 5:
                    lcd_string("Sensor Error!", LCD_LINE_1)
                    lcd_string("Check Connection", LCD_LINE_2)
            
            # Pause to reduce CPU usage
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nProgram exited")
    finally:
        lcd_string("System Shutdown", LCD_LINE_1)
        lcd_string("Goodbye!", LCD_LINE_2)
        time.sleep(1)
        
        # Clean up and close
        if 'pwm' in globals():
            pwm.stop()
        GPIO.cleanup()
        print("System shut down, GPIO cleaned up")

if __name__ == "__main__":
    main()