from services.crew_context import crew_context_window


def test_crew_context_window_keeps_recent_messages():
    history = [{"role": "user", "content": f"message {i}"} for i in range(12)]
    window = crew_context_window(history, message_limit=4, char_limit=1_000)
    assert [msg["content"] for msg in window] == [
        "message 8",
        "message 9",
        "message 10",
        "message 11",
    ]


def test_crew_context_window_keeps_latest_summary():
    history = [
        {"role": "user", "content": "[Conversation summary]\nEarlier decision"},
        {"role": "assistant", "content": "caught up"},
        *({"role": "user", "content": f"recent {i}"} for i in range(6)),
    ]
    window = crew_context_window(history, message_limit=2, char_limit=1_000)
    assert window[0]["content"].startswith("[Conversation summary]")
    assert [msg["content"] for msg in window[1:]] == ["recent 4", "recent 5"]


def test_crew_context_window_keeps_last_message_even_if_large():
    history = [
        {"role": "user", "content": "old"},
        {"role": "user", "content": "x" * 100},
    ]
    window = crew_context_window(history, message_limit=4, char_limit=10)
    assert window == [history[-1]]
