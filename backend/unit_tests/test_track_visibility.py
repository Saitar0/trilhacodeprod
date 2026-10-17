from permissions import can_view_track


def test_students_can_view_only_published_non_private_tracks():
    student = {"role": "student"}

    assert can_view_track({"status": "published", "visibility": "public"}, student)
    assert not can_view_track({"status": "published", "visibility": "private"}, student)
    assert not can_view_track({"status": "published", "visibility": "unlisted"}, student)
    assert not can_view_track({"status": "published"}, student)
    assert not can_view_track({"status": "draft", "visibility": "public"}, student)


def test_staff_can_view_private_tracks():
    assert can_view_track({"status": "published", "visibility": "private"}, {"role": "admin"})
