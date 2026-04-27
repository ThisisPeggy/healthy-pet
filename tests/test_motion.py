import unittest

from PySide6.QtCore import QPoint

from healthy_pet.pet.motion import PetMotionState


class PetMotionStateTests(unittest.TestCase):
    def test_release_drag_calculates_throw_speed_from_recent_positions(self) -> None:
        motion = PetMotionState()
        motion.start_drag(QPoint(4, 5), QPoint(10, 10))
        motion.record_mouse_position(QPoint(10, 20))
        motion.record_mouse_position(QPoint(20, 24))
        motion.record_mouse_position(QPoint(34, 36))
        motion.record_mouse_position(QPoint(50, 60))

        motion.release_drag()

        self.assertFalse(motion.dragging)
        self.assertTrue(motion.falling)
        self.assertFalse(motion.on_floor)
        self.assertEqual(motion.speed_x, 7.5)
        self.assertEqual(motion.speed_y, 9.0)
        self.assertEqual(motion.mouse_positions_x, [0, 0, 0, 0])
        self.assertEqual(motion.mouse_positions_y, [0, 0, 0, 0])

    def test_release_without_mouse_movement_starts_fall_without_throw_speed(self) -> None:
        motion = PetMotionState()
        motion.start_drag(QPoint(1, 2), QPoint(10, 10))

        motion.release_drag()

        self.assertTrue(motion.falling)
        self.assertEqual(motion.speed_x, 0.0)
        self.assertEqual(motion.speed_y, 0.0)

    def test_drag_visual_requires_actual_movement(self) -> None:
        motion = PetMotionState()
        motion.start_drag(QPoint(1, 2), QPoint(10, 10))

        self.assertFalse(motion.should_show_drag(QPoint(11, 11)))
        self.assertTrue(motion.should_show_drag(QPoint(14, 10)))

    def test_stop_on_floor_clears_fall_velocity(self) -> None:
        motion = PetMotionState(falling=True, on_floor=False, speed_x=4.0, speed_y=3.0)

        motion.stop_on_floor()

        self.assertFalse(motion.falling)
        self.assertTrue(motion.on_floor)
        self.assertEqual(motion.speed_x, 0.0)
        self.assertEqual(motion.speed_y, 0.0)


if __name__ == "__main__":
    unittest.main()
