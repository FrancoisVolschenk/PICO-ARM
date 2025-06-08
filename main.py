from machine import Pin, I2C
import time
import servo
import network
import socket

led = Pin("LED", Pin.OUT)
led.off()
grabbed = False
speed = 1

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print("Connecting", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
    print("\nConnected:", wlan.ifconfig())
    led.on()
    time.sleep(2)
    led.off()
    return wlan.ifconfig()[0]

def start_server(handler):
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Listening on", addr)

    while True:
        cl, addr = s.accept()
        print("Client connected from", addr)
        request = cl.recv(1024).decode('utf-8')
        # print("Request:", request)

        if "GET /cmd?" in request:
            cmd = request.split("GET /cmd?")[1].split(" ")[0]
            handler(cmd)
            cl.send('HTTP/1.1 200 OK\r\n')
            cl.send('Content-Type: application/json\r\n')
            cl.send('Access-Control-Allow-Origin: *\r\n')
            cl.send('Connection: close\r\n\r\n')
            cl.send('{"status": "success"}')
            cl.close()
        else:
            response = html_page()
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()

def command_handler(cmd):
    global grabbed
    global speed
    if cmd == "w":
        servos.rotate(ARM, speed_level=speed, direction='cw', duration=0.3)
    if cmd == "a":
        servos.rotate(BASE, speed_level=speed, direction='ccw', duration=0.3)
    if cmd == "s":
        servos.rotate(ARM, speed_level=speed, direction='ccw', duration=0.3)
    if cmd == "d":
        servos.rotate(BASE, speed_level=speed, direction='cw', duration=0.3)
    if cmd == "h":
        servos.rotate(ELBOW, speed_level=speed, direction='cw', duration=0.3)
    if cmd == "j":
        servos.rotate(ELBOW, speed_level=speed, direction='ccw', duration=0.3)
    if cmd == "e":
        servos.set_angle(GRIPPER, (80 if grabbed else 0))
        grabbed = not grabbed
    if "speed" in cmd:
        new_speed = int(cmd.replace("speed", ""))
        print("setting speed to", new_speed)
        speed = new_speed
    if cmd == "q":
        listen = False
    else:
        pass


def html_page():
    return """
        <!DOCTYPE html>
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Robot Arm Control</title>
                <style>
                    button {
                        background-color: darkred;
                        border-radius: 5px;
                        color: white;
                        padding: 10px 20px;
                        margin: 5px;
                        font-size: 16px;
                    }
                </style>
                <script>
                    function sendCommand(cmd) {
                        fetch(`/cmd?${cmd}`)
                            .then(response => response.json())
                            .then(data => console.log("Command sent:", cmd, data))
                            .catch(error => console.error("Error sending command:", cmd, error));
                    }
                </script>
            </head>
            <body style="background-color: dimgray;">
                <div style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <h1 style="background-color:lightslategrey;">Control Panel</h1>
                    <div style="display: flex; flex-direction: column; justify-content: center;">
                        <button onclick="sendCommand('w')">Up</button>
                    </div>
                    <div style="display: flex; flex-direction: row;">
                        <button onclick="sendCommand('a')">Left</button>
                        <button onclick="sendCommand('d')">Right</button>
                    </div>
                    <div style="display: flex; flex-direction: column; justify-content: center;">
                        <button onclick="sendCommand('s')">Down</button>
                    </div>

                    <br><br>
                    <div style="display: flex; flex-direction: column;">
                        <button onclick="sendCommand('h')">Elbow Up</button>
                        <button onclick="sendCommand('j')">Elbow Down</button>
                    </div>
                    <br>
                    <button onclick="sendCommand('e')">Toggle Gripper</button>
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; border: solid; border-radius: 5px; width: 50%;">
                        <input type="radio" id="stop" name="speed" value="0" onchange="sendCommand(`speed${this.value}`)">
                        <label for="stop">STOP</label><br>
                        <input type="radio" id="slow" name="speed" value="1" onchange="sendCommand(`speed${this.value}`)">
                        <label for="slow">SLOW</label><br>
                        <input type="radio" id="medium" name="speed" value="3" onchange="sendCommand(`speed${this.value}`)">
                        <label for="medium">MEDIUM</label>
                        <input type="radio" id="fast" name="speed" value="2" onchange="sendCommand(`speed${this.value}`)">
                        <label for="fast">FAST</label>
                    </div>
                </div>
            </body>
        </html>
        """

i2c = I2C(0, scl=Pin(1), sda=Pin(0))
servos = servo.ContinuousServos(i2c)

BASE = 0
ARM = 2
ELBOW = 4
GRIPPER = 6

servos.rotate(BASE, speed_level=1, direction='cw', duration=0.3)
servos.rotate(BASE, speed_level=1, direction='ccw', duration=0.3)

servos.rotate(ARM, speed_level=1, direction='cw', duration=0.3)
servos.rotate(ARM, speed_level=1, direction='ccw', duration=0.3)

servos.rotate(ELBOW, speed_level=1, direction='cw', duration=0.3)
servos.rotate(ELBOW, speed_level=1, direction='ccw', duration=0.3)

servos.set_angle(GRIPPER, 0)
servos.set_angle(GRIPPER, 80)
servos.set_angle(GRIPPER, 45)

try:
    ip = connect_wifi("***REMOVED***", "***REMOVED***")
    start_server(command_handler)
except:
    servos.stop(0)
    servos.stop(2)
    servos.stop(4)
