import unittest

from healthy_pet.pet.animation import PetAnimationState


class FakeGeometry:
    def __init__(self, left: int, right: int):
        self._left = left
        self._right = right

    def left(self) -> int:
        return self._left

    def right(self) -> int:
        return self._right


class PetAnimationStateTests(unittest.TestCase):
    def test_drag_and_fall_do_not_replace_base_action(self) -> None:
        animation = PetAnimationState()
        animation.start_action("walk", persistent=True)
        animation.start_action("drag", persistent=True)

        self.assertEqual(animation.restore_base_action({"idle", "walk"}), ("walk", True))

    def test_non_persistent_action_returns_to_idle_after_last_frame(self) -> None:
        animation = PetAnimationState()
        animation.start_action("angry", persistent=False)

        self.assertTrue(animation.advance_frame(2))
        self.assertFalse(animation.advance_frame(2))

    def test_persistent_action_wraps_frame_index(self) -> None:
        animation = PetAnimationState()
        animation.start_action("walk", persistent=True)

        self.assertTrue(animation.advance_frame(2))
        self.assertTrue(animation.advance_frame(2))
        self.assertEqual(animation.frame_index, 0)

    def test_walk_turns_at_range_edges(self) -> None:
        animation = PetAnimationState(walk_origin_x=100, walk_range=10, walk_step=6)

        next_x, direction = animation.next_walk_x(106)

        self.assertEqual(next_x, 110)
        self.assertEqual(direction, "left")
        self.assertEqual(animation.walk_direction, -1)

    def test_reset_walk_motion_faces_left_near_right_edge(self) -> None:
        animation = PetAnimationState(walk_range=90)

        animation.reset_walk_motion(current_x=920, width=100, geometry=FakeGeometry(0, 1000))

        self.assertEqual(animation.walk_direction, -1)
        self.assertEqual(animation.walk_frame_key(), "left_walk")


if __name__ == "__main__":
    unittest.main()
