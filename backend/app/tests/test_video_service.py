from app.services.video_service import select_representative_frames


def test_select_representative_frames_caps_count():
    frames = [{"timestamp": i, "clarity_score": i * 10} for i in range(10)]
    selected = select_representative_frames(frames, 3)
    assert len(selected) == 3
    assert selected == sorted(selected, key=lambda item: item["timestamp"])
