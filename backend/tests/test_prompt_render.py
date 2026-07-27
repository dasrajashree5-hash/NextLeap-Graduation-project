"""Prompt templates embed literal JSON braces, so str.format() cannot be used."""

from app.llm.prompts import load_prompt_spec, render_prompt

TEMPLATES_WITH_JSON = [
    ("review_analysis.v1.txt", {"text": "great app", "rating": 5}),
    ("cluster_label.v1.txt", {"reviews": "- sample review"}),
]


def test_render_keeps_literal_json_braces():
    rendered = render_prompt('{"sentiment": "positive"} for {text}', text="abc")
    assert rendered == '{"sentiment": "positive"} for abc'


def test_render_leaves_unknown_placeholders_untouched():
    assert render_prompt("{a} {b}", a="1") == "1 {b}"


def test_prompt_specs_render_without_keyerror():
    for filename, values in TEMPLATES_WITH_JSON:
        body = load_prompt_spec(filename).body
        rendered = render_prompt(body, **values)
        for key, value in values.items():
            assert "{" + key + "}" not in rendered
            assert str(value) in rendered
        assert '"sentiment"' in rendered or '"label"' in rendered
