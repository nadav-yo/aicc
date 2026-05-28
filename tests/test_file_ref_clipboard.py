from services.file_ref_clipboard import file_ref_candidates, file_refs_payload, parse_file_refs_payload


def test_file_ref_candidates_extracts_paths_from_aichs_text():
    text = (
        "However, some modules are low:\n"
        "- `services\\git_diff.py`: 77%\n"
        "- services/content.py: 85%\n"
    )

    assert file_ref_candidates(text) == [
        "services\\git_diff.py",
        "services/content.py",
    ]


def test_file_ref_candidates_accepts_sentence_punctuation():
    assert file_ref_candidates("The file you just provided is services/chat.py.") == [
        "services/chat.py"
    ]


def test_file_refs_payload_round_trips():
    payload = file_refs_payload("see services\\git_diff.py and services\\git_diff.py")

    assert parse_file_refs_payload(payload) == ["services\\git_diff.py"]


def test_file_refs_payload_ignores_invalid_json():
    assert parse_file_refs_payload(b"not json") == []
