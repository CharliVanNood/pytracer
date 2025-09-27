import math

from objects.vector3 import Vector3

class Player:
    def __init__(self):
        self.position = Vector3(0, 0, 0)
        self.rotation = Vector3(0, 0, 0)

        self.forward = self.get_forward(self.rotation.x, self.rotation.y)

    def get_forward(self, x, y):
        pitch = math.radians(x)
        yaw   = math.radians(y)

        x = math.cos(pitch) * math.sin(yaw)
        y = math.sin(pitch)
        z = math.cos(pitch) * math.cos(yaw)

        return Vector3(x, y, z)