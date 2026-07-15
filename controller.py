# Contains PID class and controller logic
import time

class PIDController:
    def __init__(self, kp, ki, kd, deadband, integral_limit):

        # for tuning
        self.kp = kp
        self.ki = ki
        self.kd = kd

        # deadband to prevent constant correction
        # integral limit to avoid windup
        self.deadband = deadband
        self.integral_limit = integral_limit

        # PID state 
        self.previous_error = 0
        self.integral = 0
        self.previous_time = None

    def calculate(self, setpoint, current_value):
        current_time = time.time()

        # avoid any division by zero if its initializing for first time
        if self.previous_time is None:
            dt = 0.033
        else:
            dt = current_time - self.previous_time

        # update state
        self.previous_time = current_time

        error = setpoint - current_value

        if abs(error) < self.deadband:
            error = 0
            # If spending lots of time in deadband, bleed integral
            # to avoid jumps after leaving deadband
            self.integral *= 0.9

        P = self.kp * error

        self.integral += error * dt

        # Apply windup guard
        if self.integral > self.integral_limit:
            self.integral = self.integral_limit
        elif self.integral < -self.integral_limit:
            self.integral = -self.integral_limit

        I = self.ki * self.integral

        derivative = (error - self.self.previous_error) / dt

        D = self.kd * derivative

        self.previous_error = error

        # number of degrees to add or subtract from current servo pos
        control_effort = P + I + D

        return control_effort
    
    def reset(self):
        # if person leaves frame/YOLO detects no bodies
        self.previous_error = 0
        self.previous_time = None
        self.integral = 0