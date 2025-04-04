#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
servo_control.py - 伺服电机网页远程控制的纯Python后端API服务器
使用Python内置的http.server模块提供API服务
'''

import RPi.GPIO as GPIO
import time
import socket
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 伺服电机引脚设置
SERVO_PIN = 18  # 使用GPIO18作为PWM输出引脚，可以根据实际连接修改

# 伺服电机脉冲宽度范围（微秒）- 扩展角度范围
MIN_PULSE_WIDTH = 450   # 对应-100度
MAX_PULSE_WIDTH = 2500  # 对应270度
MID_PULSE_WIDTH = 1500  # 对应90度

# Web服务器端口
PORT = 5500

# 存储舵机当前角度
current_angle = 90

# 将脉冲宽度转换为占空比
def pulse_width_to_duty_cycle(pulse_width):
    return pulse_width / 20000 * 100

# 将角度转换为占空比 - 扩展角度范围为-100到270度
def angle_to_duty_cycle(angle):
    # 限制在-100到270度范围内
    if angle < -100:
        angle = -100
    elif angle > 270:
        angle = 270
    
    # 将角度映射到脉冲宽度
    # 使用分段映射以提高精度
    if angle < 90:
        pulse_width = MID_PULSE_WIDTH + (angle - 90) * (MID_PULSE_WIDTH - MIN_PULSE_WIDTH) / 190
    else:
        pulse_width = MID_PULSE_WIDTH + (angle - 90) * (MAX_PULSE_WIDTH - MID_PULSE_WIDTH) / 180
    
    # 将脉冲宽度转换为占空比
    duty_cycle = pulse_width_to_duty_cycle(pulse_width)
    return duty_cycle

# 初始化GPIO和PWM
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    
    # 创建PWM实例，频率为50Hz（舵机标准频率）
    pwm = GPIO.PWM(SERVO_PIN, 50)
    pwm.start(0)  # 以占空比0开始（不转动）
    return pwm

# 获取树莓派的IP地址
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 不需要真的发送数据，只是需要建立路由
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# 设置伺服电机角度
def set_servo_angle(angle):
    global current_angle
    try:
        angle = int(angle)
        if angle < -100 or angle > 270:
            return {"status": "error", "message": "角度必须在-100到270之间"}
        
        duty_cycle = angle_to_duty_cycle(angle)
        pwm.ChangeDutyCycle(duty_cycle)
        current_angle = angle
        time.sleep(0.5)  # 等待舵机移动到位
        pwm.ChangeDutyCycle(0)  # 停止PWM信号，防止舵机抖动
        
        return {"status": "success", "angle": angle}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 设置预设位置
def set_preset_position(position):
    if position == 'far_left':
        angle = -100
    elif position == 'left':
        angle = 0
    elif position == 'center':
        angle = 90
    elif position == 'right':
        angle = 180
    elif position == 'far_right':
        angle = 270
    else:
        return {"status": "error", "message": "无效的预设位置"}
    
    result = set_servo_angle(angle)
    if result["status"] == "success":
        result["position"] = position
    
    return result

# 执行扫描动作
def sweep_servo(start_angle, end_angle, step, delay):
    global current_angle
    try:
        start_angle = int(start_angle)
        end_angle = int(end_angle)
        step = int(step)
        delay = float(delay)
        
        if start_angle < -100 or start_angle > 270 or end_angle < -100 or end_angle > 270:
            return {"status": "error", "message": "角度必须在-100到270之间"}
        
        # 确定步进方向
        if start_angle <= end_angle:
            angle_range = range(start_angle, end_angle + 1, step)
        else:
            angle_range = range(start_angle, end_angle - 1, -step)
        
        # 执行扫描
        for angle in angle_range:
            duty_cycle = angle_to_duty_cycle(angle)
            pwm.ChangeDutyCycle(duty_cycle)
            current_angle = angle
            time.sleep(delay)
        
        # 停止PWM信号，防止舵机抖动
        pwm.ChangeDutyCycle(0)
        
        return {"status": "success", "start": start_angle, "end": end_angle}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# HTTP请求处理器
class ServoRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='application/json'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')  # 允许跨域请求
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _set_error_headers(self, error_code=400):
        self.send_response(error_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 只处理API请求，因为前端页面是从客户端电脑上加载的
        if path == '/api/get_angle':
            self._set_headers('application/json')
            response = json.dumps({"angle": current_angle})
            self.wfile.write(response.encode())
        else:
            self._set_error_headers(404)
            response = json.dumps({"status": "error", "message": "未找到请求的资源"})
            self.wfile.write(response.encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            data = json.loads(post_data.decode())
            
            if path == '/api/set_angle':
                angle = data.get('angle', 90)
                response = set_servo_angle(angle)
                
            elif path == '/api/preset':
                position = data.get('position', 'center')
                response = set_preset_position(position)
                
            elif path == '/api/sweep':
                start_angle = data.get('start', -100)
                end_angle = data.get('end', 270)
                step = data.get('step', 10)
                delay = data.get('delay', 0.1)
                response = sweep_servo(start_angle, end_angle, step, delay)
                
            else:
                self._set_error_headers(404)
                response = {"status": "error", "message": "未知的API端点"}
                
            self._set_headers('application/json')
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError:
            self._set_error_headers(400)
            self.wfile.write(json.dumps({"status": "error", "message": "无效的JSON数据"}).encode())
    
    def do_OPTIONS(self):
        # 处理预检请求，对跨域请求非常重要
        self._set_headers()

# 主函数
def main():
    global pwm
    
    try:
        # 设置伺服电机
        pwm = setup()
        
        # 获取IP地址
        ip_address = get_ip_address()
        
        # 启动Web服务器
        server_address = ('', PORT)
        httpd = HTTPServer(server_address, ServoRequestHandler)
        print(f"伺服电机API服务已启动！")
        print(f"API地址: http://{ip_address}:{PORT}")
        print(f"角度范围: -100° 到 270°")
        print(f"请确保前端页面中的API_BASE_URL设置为: 'http://{ip_address}:{PORT}'")
        print(f"按Ctrl+C退出")
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n程序已退出")
    finally:
        # 停止PWM并清理GPIO
        try:
            pwm.stop()
            GPIO.cleanup()
        except:
            pass

if __name__ == '__main__':
    main()