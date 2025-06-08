# continuous_servo.py
import pca9685
import time

class ContinuousServos:
    def __init__(self, i2c, address=0x40, freq=50):
        self.freq = freq
        self.pca9685 = pca9685.PCA9685(i2c, address)
        self.pca9685.freq(freq)

        # ~20ms period at 50Hz → 1 count = ~4.88us
        self.STOP = self._us_to_duty(1500)
        self.SPEEDS = {
            0: 0,
            1: self._us_to_duty(150),   # slow
            2: self._us_to_duty(300),   # medium
            3: self._us_to_duty(450),   # fast
            4: self._us_to_duty(600),   # max
        }

    def _us_to_duty(self, us):
        period_us = 1000000 / self.freq
        return int(4095 * us / period_us)

    def rotate(self, index, speed_level=0, direction="cw", duration=0.5):
        if speed_level not in self.SPEEDS:
            raise ValueError("Speed level must be between 0 and 4")
        
        offset = self.SPEEDS[speed_level]

        if direction == "cw":
            duty = self.STOP - offset
        elif direction == "ccw":
            duty = self.STOP + offset
        else:
            raise ValueError("Direction must be 'cw' or 'ccw'")

        # Send the PWM signal to rotate the servo
        self.pca9685.duty(index, duty)

        # Wait for desired duration
        time.sleep(duration)

        # Stop the servo
        self.pca9685.duty(index, self.STOP)

    def set_move(self, index, speed_level=0, direction="cw"):
        if speed_level not in self.SPEEDS:
            raise ValueError("Speed level must be between 0 and 4")
        
        offset = self.SPEEDS[speed_level]

        if direction == "cw":
            duty = self.STOP - offset
        elif direction == "ccw":
            duty = self.STOP + offset
        else:
            raise ValueError("Direction must be 'cw' or 'ccw'")

        # Send the PWM signal to rotate the servo
        self.pca9685.duty(index, duty)


    def set_angle(self, index, degrees):
        """
        Direct angle-to-PWM method based on 16-bit PWM style formula:
        duty_u16 = int(((6553/180) * degrees) + 1638)
        We convert this to 12-bit PCA9685 range.
        """
        duty_u16 = int(((6553 / 180) * degrees) + 1638)
        duty_12bit = duty_u16 >> 4  # Convert from 16-bit to 12-bit
        duty_12bit = min(4095, max(0, duty_12bit))  # Clamp
        self.pca9685.duty(index, duty_12bit)

    def stop(self, index):
        self.pca9685.duty(index, self.STOP)
