"""CLI behaviour: text, file, stdin, JSON spans, SSML and options."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from falabr.cli import build_parser, main


def test_text_argument(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["comprei", "1.234,56", "reais"]) == 0
    assert capsys.readouterr().out.strip() == (
        "comprei mil duzentos e trinta e quatro vírgula cinquenta e seis reais"
    )


def test_fraction_ordinal_and_roman(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["3/4", "3º", "1ª", "século", "XXI"]) == 0
    assert capsys.readouterr().out.strip() == ("três quartos terceiro primeira século vinte e um")


def test_regnal_roman_option(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Dom", "Pedro", "II", "--roman-context", "regnal"]) == 0
    assert capsys.readouterr().out.strip() == "Dom Pedro segundo"


def test_number_options(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["14", "3,14", "--catorze", "--decimal-mode", "digits"]) == 0
    assert capsys.readouterr().out.strip() == "catorze três vírgula um quatro"


def test_json_spans(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["total:", "12,5", "reais", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["text"] == "total: doze vírgula cinco reais"
    assert payload["spans"] == [
        {
            "start": 7,
            "end": 11,
            "original": "12,5",
            "spoken": "doze vírgula cinco",
        }
    ]


def test_ssml_escaping(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["a", "&", "b", "3", "--ssml"]) == 0
    assert capsys.readouterr().out.strip() == "<speak>a &amp; b três</speak>"


def test_file_input(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    source = tmp_path / "texto.txt"
    source.write_text("foram 2.000 pessoas", encoding="utf-8")
    assert main(["-f", str(source)]) == 0
    assert capsys.readouterr().out.strip() == "foram dois mil pessoas"


def test_stdin_input(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("século XXI"))
    assert main([]) == 0
    assert capsys.readouterr().out.strip() == "século vinte e um"


def test_invalid_roman_token_is_left_untouched(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["IIII", "e", "5"]) == 0
    assert capsys.readouterr().out.strip() == "IIII e cinco"


def test_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["texto"])
    assert args.json is False
    assert args.ssml is False
    assert args.decimal_mode == "cardinal"
