#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Read DHT11 sensor data using dht11 library and display on LCD 1602A
English version (no Chinese characters)
'''

import RPi.GPIO as GPIO
import dht11
import time

# LCD 1602A pin configuration (as provided by user)
LCD_RS = 26  # GPIO26 (pin 37)
LCD_E = 19   # GPIO19 (pin 35)
LCD_D4 = 13  # GPIO13 (pin 33)
LCD_D5 = 6   # GPIO6 (pin 31)
LCD_D6 = 5   # GPIO5 (pin 29)
LCD_D7 = 11  # GPIO11 (pin 23)

# DHT11 sensor pin
DHT_PIN = 4  # GPIO4 (physical pin 7)

# LCD constants
LCD_WIDTH = 16    # LCD character width
LCD_LINE_1 = 0x80 # LCD RAM address for 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for 2nd line
LCD_CHR = True    # Send data
LCD_CMD = False   # Send command
E_PULSE = 0.0005  # E pulse width
E_DELAY = 0.0005  # E delay

def lcd_init():
    '''Initialize LCD display'''
    # Set GPIO mode
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LCD_E, GPIO.OUT)
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_D4, GPIO.OUT)
    GPIO.setup(LCD_D5, GPIO.OUT)
    GPIO.setup(LCD_D6, GPIO.OUT)
    GPIO.setup(LCD_D7, GPIO.OUT)

    # Initialize display
    lcd_byte(0x33, LCD_CMD) # 110011 Initialize
    lcd_byte(0x32, LCD_CMD) # 110010 Initialize
    lcd_byte(0x06, LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD) # 001100 Display On, Cursor Off
    lcd_byte(0x28, LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    '''Send byte to LCD'''
    # Set RS pin
    GPIO.output(LCD_RS, mode)

    # Send high 4 bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Enable pulse
    lcd_toggle_enable()

    # Send low 4 bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Enable pulse
    lcd_toggle_enable()

def lcd_toggle_enable():
    '''Toggle enable pulse'''
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)

def lcd_string(message, line):
    '''Send string to LCD'''
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

def main():
    '''Main function'''
    try:
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Initialize LCD
        lcd_init()
        print("LCD initialized")
        
        # Initialize DHT11 instance
        instance = dht11.DHT11(pin=DHT_PIN)
        
        # Display welcome message
        lcd_string("Temp&Humid System", LCD_LINE_1)
        lcd_string("Starting...", LCD_LINE_2)
        time.sleep(2)
        
        print("Starting to read DHT11 sensor data...")
        error_count = 0
        
        while True:
            # Read DHT11 sensor data
            result = instance.read()
            
            if result.is_valid():
                # Get temperature and humidity values
                temp = result.temperature
                humidity = result.humidity
                
                # Format temperature and humidity strings
                temp_str = "Temp: {}C".format(temp)
                hum_str = "Humidity: {}%".format(humidity)
                
                # Display data on LCD
                lcd_string(temp_str, LCD_LINE_1)
                lcd_string(hum_str, LCD_LINE_2)
                
                # Print data to terminal
                print("Temperature: {}°C, Humidity: {}%".format(temp, humidity))
                
                # Reset error count
                error_count = 0
            else:
                error_count += 1
                print("Failed to read sensor, attempt: {}".format(error_count))
                
                if error_count > 5:
                    lcd_string("Sensor Error!", LCD_LINE_1)
                    lcd_string("Check Connection", LCD_LINE_2)
            
            # Update every 2 seconds (DHT11 manual suggests at least 1s)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nProgram exited")
    finally:
        lcd_string("System Shutdown", LCD_LINE_1)
        lcd_string("Goodbye!", LCD_LINE_2)
        time.sleep(1)
        GPIO.cleanup()

if __name__ == "__main__":
    main()#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Read DHT11 sensor data using dht11 library and display on LCD 1602A
English version (no Chinese characters)
'''

import RPi.GPIO as GPIO
import dht11
import time

# LCD 1602A pin configuration (as provided by user)
LCD_RS = 26  # GPIO26 (pin 37)
LCD_E = 19   # GPIO19 (pin 35)
LCD_D4 = 13  # GPIO13 (pin 33)
LCD_D5 = 6   # GPIO6 (pin 31)
LCD_D6 = 5   # GPIO5 (pin 29)
LCD_D7 = 11  # GPIO11 (pin 23)

# DHT11 sensor pin
DHT_PIN = 4  # GPIO4 (physical pin 7)

# LCD constants
LCD_WIDTH = 16    # LCD character width
LCD_LINE_1 = 0x80 # LCD RAM address for 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for 2nd line
LCD_CHR = True    # Send data
LCD_CMD = False   # Send command
E_PULSE = 0.0005  # E pulse width
E_DELAY = 0.0005  # E delay

def lcd_init():
    '''Initialize LCD display'''
    # Set GPIO mode
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LCD_E, GPIO.OUT)
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_D4, GPIO.OUT)
    GPIO.setup(LCD_D5, GPIO.OUT)
    GPIO.setup(LCD_D6, GPIO.OUT)
    GPIO.setup(LCD_D7, GPIO.OUT)

    # Initialize display
    lcd_byte(0x33, LCD_CMD) # 110011 Initialize
    lcd_byte(0x32, LCD_CMD) # 110010 Initialize
    lcd_byte(0x06, LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD) # 001100 Display On, Cursor Off
    lcd_byte(0x28, LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    '''Send byte to LCD'''
    # Set RS pin
    GPIO.output(LCD_RS, mode)

    # Send high 4 bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Enable pulse
    lcd_toggle_enable()

    # Send low 4 bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Enable pulse
    lcd_toggle_enable()

def lcd_toggle_enable():
    '''Toggle enable pulse'''
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)

def lcd_string(message, line):
    '''Send string to LCD'''
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

def main():
    '''Main function'''
    try:
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Initialize LCD
        lcd_init()
        print("LCD initialized")
        
        # Initialize DHT11 instance
        instance = dht11.DHT11(pin=DHT_PIN)
        
        # Display welcome message
        lcd_string("Temp&Humid System", LCD_LINE_1)
        lcd_string("Starting...", LCD_LINE_2)
        time.sleep(2)
        
        print("Starting to read DHT11 sensor data...")
        error_count = 0
        
        while True:
            # Read DHT11 sensor data
            result = instance.read()
            
            if result.is_valid():
                # Get temperature and humidity values
                temp = result.temperature
                humidity = result.humidity
                
                # Format temperature and humidity strings
                temp_str = "Temp: {}C".format(temp)
                hum_str = "Humidity: {}%".format(humidity)
                
                # Display data on LCD
                lcd_string(temp_str, LCD_LINE_1)
                lcd_string(hum_str, LCD_LINE_2)
                
                # Print data to terminal
                print("Temperature: {}°C, Humidity: {}%".format(temp, humidity))
                
                # Reset error count
                error_count = 0
            else:
                error_count += 1
                print("Failed to read sensor, attempt: {}".format(error_count))
                
                if error_count > 5:
                    lcd_string("Sensor Error!", LCD_LINE_1)
                    lcd_string("Check Connection", LCD_LINE_2)
            
            # Update every 2 seconds (DHT11 manual suggests at least 1s)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nProgram exited")
    finally:
        lcd_string("System Shutdown", LCD_LINE_1)
        lcd_string("Goodbye!", LCD_LINE_2)
        time.sleep(1)
        GPIO.cleanup()

if __name__ == "__main__":
    main()