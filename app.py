from flask import Flask, jsonify, render_template
import RPi.GPIO as GPIO
import time
import threading

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
solenoid_pin = 15
GPIO.setup(solenoid_pin, GPIO.OUT)
GPIO.output(solenoid_pin, GPIO.LOW)  # Keep solenoid OFF initially!

# Thread lock for solenoid
lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solenoid/on')
def turn_on():
    GPIO.output(solenoid_pin, GPIO.HIGH)
    return jsonify(status='Solenoid is ON')

@app.route('/solenoid/off')
def turn_off():
    GPIO.output(solenoid_pin, GPIO.LOW)
    return jsonify(status='Solenoid is OFF')

@app.route('/solenoid/tap/<int:num_taps>')
def tap_solenoid(num_taps):
    if num_taps in [1, 2, 3, 5]:
        threading.Thread(target=rapid_taps, args=(num_taps,)).start()
        return jsonify(status=f'Rapid {num_taps} taps executed')
    else:
        return jsonify(status='Invalid number of taps'), 400

def rapid_taps(num_taps):
    with lock:
        for _ in range(num_taps):
            GPIO.output(solenoid_pin, GPIO.HIGH)
            time.sleep(0.05)
            GPIO.output(solenoid_pin, GPIO.LOW)
            time.sleep(0.08)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()
