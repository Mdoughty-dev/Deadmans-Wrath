def update_player_animation(state, animations):
    visual = state["player_visual_state"]

    action = visual["action"]
    facing = visual["facing"]
    key = f"{action}_{facing}"

    frames = animations.get(key)

    if not frames:
        return

    visual["frame_timer"] += 1

    if visual["frame_timer"] >= visual["animation_speed"]:
        visual["frame_timer"] = 0
        visual["frame_index"] = (visual["frame_index"] + 1) % len(frames)


def get_current_player_frame(state, animations, fallback_image):
    visual = state["player_visual_state"]

    action = visual["action"]
    facing = visual["facing"]
    key = f"{action}_{facing}"

    frames = animations.get(key)

    # fallback if missing (important for now)
    if not frames:
        frames = animations.get(f"{action}_down") or [fallback_image]

    frame_index = visual["frame_index"] % len(frames)
    return frames[frame_index]


def reset_player_visual_state(state, action="idle", facing=None):
    visual = state["player_visual_state"]

    visual["action"] = action
    if facing is not None:
        visual["facing"] = facing
    visual["frame_index"] = 0
    visual["frame_timer"] = 0