from app.services.dedup import normalize, text_hash


def test_normalize_strips_links_and_punctuation():
    a = normalize("🔥 NEW Drum Kit!!! https://t.me/abc @chan  Download now")
    assert a == "new drum kit download now"


def test_hash_ignores_channel_ads():
    a = text_hash("Trap Drum Kit 2024 — 120 sounds, kicks and snares @channel_a")
    b = text_hash("Trap Drum Kit 2024 — 120 sounds, kicks and snares https://t.me/channel_b")
    assert a == b and a is not None


def test_short_text_has_no_hash():
    assert text_hash("kit") is None
