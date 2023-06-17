from machine import Pin, ADC, SoftI2C
from time import sleep
import time
import urequests
import json
import network
import uasyncio as asyncio
import utime
import ntptime
import math
import machine

WIFI_ssd = "ssd"
WIFI_pass = "pass"

main_url = "https://your-api-link.onrender.com/"
sub_url_post = "data-post"
sub_url_get = "open-actual"

Window_status = 2
Water_status = "0"
Water_status_last = "0"


# API comunication
# ------------------------------------------------------------------------------------------------------------------------------
async def send_put_request(data, url):
    try:
      response = urequests.put(url, json=data)
      return rsponse.code
    except:
      pass
    
    
async def download_and_extract_data():
    URL = main_url + sub_url_get                  # Make an HTTP GET request to the API
    response = urequests.get(URL)
    response_content = response.content           # Read the response content
    response.close()                              # Close the HTTP connection
    json_data = json.loads(response_content)      # Parse the JSON data
    extracted_data_open = json_data["open"]            # Extract the required data from the JSON
    extracted_data_water = json_data["waterid"]
    return [extracted_data_open, extracted_data_water]
    
 
async def async_send(Temp=0, Air=0, Soil=0, Wind=0):
  loop = asyncio.get_event_loop()
  i = 0
  while i < 1:
    URL = main_url + sub_url_post
    now = get_time()
    
    payload = {"Temperature": Temp, "AirHumidity": Air, "SoilHumidity": Soil, "WindowsOpened": Wind, "CreationDateTime": now}
    gc.collect()
    await loop.create_task(send_put_request(payload, URL))
    i = i + 1
    time.sleep(1)
    
    
async def async_get():
  loop = asyncio.get_event_loop()
  i = 0
  while i < 1:
    gc.collect()
    data = await loop.create_task(download_and_extract_data())
    global Window_status
    global Water_status
    Window_status = int(data[0])
    Water_status = str(data[1])
    i = i + 1
    time.sleep(1)
    
    
def get_time():
  try:
    ntptime.settime()                                                       # Synchronize with an NTP server
    timezone_offset = 7200                                                  # Set the desired timezone offset in seconds
    current_timestamp = utime.time()
    adjusted_timestamp = current_timestamp + timezone_offset                # Apply the timezone offset
    current_time = utime.localtime(adjusted_timestamp)                      # Get the current date and time
    year, month, day, hour, minute, second, weekday, yearday = current_time # Extract individual components of the date and time
    d = str(day)
    m = str(month)
    y = str(year)
    h = str(hour)
    mi = str(minute)
    s = str(second)
    ret = y + "-" + m + "-" + d + " " + h + ":" + mi + ":" + s
    return ret
  except:
    return "0-0-0 0:0:0"
  
 
def api_refresh(Temp=0, Air=0, Soil=0, Wind=0):
  # Create an event loop
  loop = asyncio.get_event_loop()
  # Run the download_and_extract_data function in the event loop
  loop.run_until_complete(async_send(Temp=Temp, Air=Air, Soil=Soil, Wind=Wind))
  loop.run_until_complete(async_get())
  # Close the event loop
  loop.close()
  
# ------------------------------------------------------------------------------------------------------------------------------

class Termistor():
    def __init__(self, pin=34):
        self.mesurement = ADC(Pin(pin))
        self.mesurement.atten(ADC.ATTN_11DB)
        self.a = 0.00003173
        self.c = 847.1
        self.d = -20.19

    def get_temperature(self):
        termistor_value = self.mesurement.read()
        voltage = termistor_value * 3.3 / 4095
        R = (voltage * 12000) / (5 - voltage)
        temp = self.d * math.log(self.a * (R - self.c))
        return temp
# ------------------------------------------------------------------------------------------------------------------------------


class Display():
    def __init__(self, pin1=22, pin2=21):
        i2c = SoftI2C(scl=Pin(pin1), sda=Pin(pin2))
        oled_width = 128
        oled_height = 64
        self.oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

    def oled_print(self, text, cursory=0, cursorx=0):
        self.oled.text(text, cursorx, cursory)
        self.oled.show()
        
    def oled_clear(self):
        self.oled.fill(0)

# ------------------------------------------------------------------------------------------------------------------------------

class ServoMotor():
    def __init__(self, pin=13):
        self.motor = Servo(pin=pin)

    def move_from_to(self, angleFrom, angleTo):
        if angleFrom > angleTo:
            add = -1
        else:
            add = 1
        for i in range(abs(angleTo - angleFrom)):
            angleFrom = angleFrom + add
            self.motor.move(angleFrom)
            time.sleep(0.15)
            
    def write(self, angle):
      self.motor.move(angle)


# ------------------------------------------------------------------------------------------------------------------------------

class AirSensor():
  def __init__(self):
    self.i2c_addr = 0x44

  # Function to write data to I2C device
  def i2c_write(self, i2c_addr, tx_bytes):
      i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))  # Initialize I2C interface
      i2c.writeto(i2c_addr, bytes(tx_bytes))  # Write tx_bytes to the I2C device at i2c_addr

  # Function to read data from I2C device
  def i2c_read(self, i2c_addr, number_of_bytes):
      i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))  # Initialize I2C interface
      rx_bytes = i2c.readfrom(i2c_addr, number_of_bytes)  # Read number_of_bytes from the I2C device at i2c_addr
      return list(rx_bytes)  # Convert received bytes to a list of integers

  def get_temperature(self):
    # Write command to initiate measurement
    self.i2c_write(self.i2c_addr, [0xFD])

    # Wait for sensor to complete measurement
    time.sleep(0.01)

    # Read measurement data from the sensor
    rx_bytes = self.i2c_read(self.i2c_addr, 6)

    # Extract temperature and humidity values from received bytes
    t_ticks = rx_bytes[0] * 256 + rx_bytes[1]
    checksum_t = rx_bytes[2]
    rh_ticks = rx_bytes[3] * 256 + rx_bytes[4]
    checksum_rh = rx_bytes[5]

    # Convert ticks to temperature and humidity values
    t_degC = -45 + 175 * t_ticks / 65535
    rh_pRH = -6 + 125 * rh_ticks / 65535

    # Ensure humidity value is within the valid range
    if rh_pRH > 100:
        rh_pRH = 100
    if rh_pRH < 0:
        rh_pRH = 0
    return [t_degC, rh_pRH]

#--------------------------------------------------------------

def run_pump(ts):
  pin_number = 25
  pin = Pin(pin_number, Pin.OUT)
  pin.value(1)
  time.sleep(ts)
  pin.value(0)
  
#--------------------------------------------------------------

def soil():
  sensor_pin = 36
  adc = ADC(Pin(sensor_pin))
  sensor_analog = adc.read()
  print("analog: " + str(sensor_analog))
  _moisture = ((sensor_analog / 4095.00) * 100)
  return float(_moisture)
  
#--------------------------------------------------------------
  
def cut_number(num):
  snum = str(num)
  parts = snum.split(".")
  temp = str(parts[0] + "." + parts[1][0])
  temp_f = float(temp)
  return temp_f
  
  
  

def main():
  global Water_status
  global Water_status_last
  motor1 = ServoMotor(pin=13)
  motor2 = ServoMotor(pin=14)
  
  air = AirSensor()
  
  
  termistor = Termistor(pin=34)

  actualPosition = 100
  lastTemp = 20

  rng = 1000
  target = 100
  for i in range(rng):
    moist = cut_number(soil())
    temper = termistor.get_temperature()
    temp_f = cut_number(temper)
    data = air.get_temperature()
    sensor_temp = cut_number(float(data[0]))
    sensor_hum = cut_number(float(data[1]))
    print("Temp_air_sensor: " + str(sensor_temp))
    print("Temp_termistor: " + str(temper))
    print("Hum_air_sensor: " + str(sensor_hum)+ "%")
    print("Soil_hum: " + str(moist)+ "%")
    print(i)

    # Get the first part of the resulting list
    if Water_status_last != Water_status:
      run_pump(1)
      Water_status_last = Water_status
    
    
    if temper < 20:
      temper = 20
    if temper > 30:
      temper = 30
    if int(Window_status) == 1:
      temper = 29
    if int(Window_status) == 3:
      temper = 20
    if abs(lastTemp - temper)> 0.5:
      lastTarget = (lastTemp-20) * 4 + 100
      target = (temper-20) * 4 + 100
      lastTemp = temper
      motor1.move_from_to(lastTarget, target)
      motor2.move_from_to(lastTarget-10, target-10)
    
    percent = str(((target-100)/40)*100)
    parts = percent.split(".")
    # Get the first part of the resulting list
    percent = str(parts[0] + "." + parts[1][0])
    
    percent_f = float(percent)
    print("Opened: " + str(percent_f) + "%")
    if i == rng-1:
      motor1.move_from_to(lastTarget, 100)
      motor2.move_from_to(lastTarget-10, 90) 
    api_refresh(Temp=temp_f, Wind=percent_f, Air=sensor_hum, Soil=moist)
    time.sleep(10)
    if i == 0:
      Water_status_last = Water_status
  
  
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
while not wlan.isconnected():
    try:
        wlan.connect(WIFI_ssd, WIFI_pass)
        time.sleep(1)  # Add a 1-second delay before the next connection attempt
    except OSError as e:
        print("Error connecting to Wi-Fi:", e)
        time.sleep(1)
print("Wi-Fi connected:", wlan.ifconfig())
main()









