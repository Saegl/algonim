class EasingTransition:
    def __init__(self, seconds, amount, object, easing_function, direction):
        """
        :param seconds: Duration of the transition.
        :param amount: Total change in distance.
        :param object: The object being transitioned.
        :param easing_function: A function that takes a normalized time `t` (0 to 1) and returns an eased value.
        :param direction: A tuple (dx, dy) specifying the direction of movement. Must be a normalized vector.
        """
        self.seconds_spent = 0.0
        self.seconds_limit = seconds
        self.amount = amount
        self.object = object
        self.start_x = object.x
        self.start_y = object.y
        self.easing_function = easing_function

        # Normalize the direction vector
        direction_magnitude = (direction[0] ** 2 + direction[1] ** 2) ** 0.5
        if direction_magnitude == 0:
            raise ValueError("Direction vector cannot be zero.")
        self.direction = (
            direction[0] / direction_magnitude,
            direction[1] / direction_magnitude,
        )

    def init_step(self):
        self.start_x = self.object.x
        self.start_y = self.object.y

    def step(self, delta: float):
        """
        Update the transition progress based on time passed.
        :param delta: Time increment (e.g., frame time).
        """
        if self.seconds_spent == 0.0:
            self.init_step()

        self.seconds_spent += delta
        if self.seconds_spent > self.seconds_limit:
            self.seconds_spent = self.seconds_limit
            return True

        t = self.seconds_spent / self.seconds_limit
        eased_t = self.easing_function(t)

        delta_distance = self.amount * eased_t
        target_x = self.start_x + self.direction[0] * delta_distance
        target_y = self.start_y + self.direction[1] * delta_distance

        self.object.set_x(target_x)
        self.object.set_y(target_y)

        return False


def cubic_ease_in_out(t):
    if t < 0.5:
        return 4 * t * t * t
    return 1 - (-2 * t + 2) ** 3 / 2


def linear_ease(t):
    return t
