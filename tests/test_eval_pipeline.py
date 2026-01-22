from __future__ import annotations

import pathlib
import tempfile


from eval_pipeline.specs import ChallengeLevel, Framework, GeneratedAppSpec
from eval_pipeline.prompts import build_generation_prompt
from eval_pipeline.gates import gate1_compile
from eval_pipeline.__main__ import _csv_list


class TestFrameworkEnum:
    def test_framework_values(self):
        expected = {"streamlit", "gradio", "shiny", "panel", "dash"}
        actual = {f.value for f in Framework}
        assert actual == expected

    def test_nicegui_not_in_frameworks(self):
        values = [f.value for f in Framework]
        assert "nicegui" not in values


class TestChallengeLevelEnum:
    def test_challenge_level_values(self):
        expected = {"beginner", "intermediate", "advanced", "expert"}
        actual = {c.value for c in ChallengeLevel}
        assert actual == expected


class TestCsvList:
    def test_simple_csv(self):
        assert _csv_list("a,b,c") == ["a", "b", "c"]

    def test_csv_with_spaces(self):
        result = _csv_list("a, b , c")
        assert result == ["a", "b", "c"]

    def test_empty_values_filtered(self):
        result = _csv_list("a,,b,")
        assert result == ["a", "b"]

    def test_empty_string(self):
        assert _csv_list("") == []


class TestBuildGenerationPrompt:
    def test_prompt_contains_framework(self):
        prompt = build_generation_prompt(
            framework=Framework.streamlit,
            level=ChallengeLevel.beginner,
            host="127.0.0.1",
            port=8501,
        )
        assert "streamlit" in prompt.lower()

    def test_prompt_contains_host_and_port(self):
        prompt = build_generation_prompt(
            framework=Framework.dash,
            level=ChallengeLevel.beginner,
            host="127.0.0.1",
            port=9000,
        )
        assert "127.0.0.1" in prompt
        assert "9000" in prompt

    def test_all_frameworks_have_prompts(self):
        for framework in Framework:
            prompt = build_generation_prompt(
                framework=framework,
                level=ChallengeLevel.beginner,
                host="127.0.0.1",
                port=8501,
            )
            assert len(prompt) > 100


class TestGate1Compile:
    def test_valid_python_passes(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(b"print('hello')\n")
            f.flush()
            result = gate1_compile(pathlib.Path(f.name))
            assert result.ok is True
            assert result.error is None

    def test_invalid_python_fails(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(b"def foo(\n")
            f.flush()
            result = gate1_compile(pathlib.Path(f.name))
            assert result.ok is False
            assert result.error is not None

    def test_syntax_error_reported(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(b"if True\n    pass\n")
            f.flush()
            result = gate1_compile(pathlib.Path(f.name))
            assert result.ok is False
            assert "SyntaxError" in result.error


class TestGeneratedAppSpec:
    def test_spec_creation(self):
        spec = GeneratedAppSpec(
            code="print('hello')",
            run_command="python app.py",
            requirements_txt="streamlit>=1.0",
            instructions="Run with python app.py",
        )
        assert spec.code == "print('hello')"
        assert spec.run_command == "python app.py"


class TestSafeDirName:
    def test_safe_dir_name_alphanumeric(self):
        from eval_pipeline.runner import _safe_dir_name
        result = _safe_dir_name("us.anthropic.claude-sonnet-4-5-20250929-v1:0")
        assert result == "us.anthropic.claude-sonnet-4-5-20250929-v10"

    def test_safe_dir_name_removes_special_chars(self):
        from eval_pipeline.runner import _safe_dir_name
        result = _safe_dir_name("model/with/slashes")
        assert "/" not in result
