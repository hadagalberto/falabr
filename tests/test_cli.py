"""CLI behaviour: text, file, stdin, JSON spans, SSML, options and full entities.

Since milestone 3 the CLI goes through the same composed pipeline as the API,
so these vectors also guard that the two surfaces never diverge.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from falabr.cli import build_parser, main


def test_text_argument(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["comprei", "1.234,56", "reais"]) == 0
    assert capsys.readouterr().out.strip() == (
        "comprei mil duzentos e trinta e quatro reais e cinquenta e seis centavos"
    )


def test_fraction_ordinal_and_roman(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["3/4", "3º", "1ª", "século", "XXI"]) == 0
    assert capsys.readouterr().out.strip() == ("três quartos terceiro primeira século vinte e um")


def test_regnal_roman_option(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Dom", "Pedro", "II", "--roman-context", "regnal"]) == 0
    assert capsys.readouterr().out.strip() == "Dom Pedro segundo"


def test_roman_context_option_is_functional(capsys: pytest.CaptureFixture[str]) -> None:
    """--roman-context regnal forces regnal reading outside the usual cues."""
    assert main(["IX", "--roman-context", "regnal"]) == 0
    assert capsys.readouterr().out.strip() == "nono"


def test_number_options(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["14", "3,14", "--catorze", "--decimal-mode", "digits"]) == 0
    assert capsys.readouterr().out.strip() == "catorze três vírgula um quatro"


def test_emoji_option(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Olá", "😀", "--emoji-mode", "describe"]) == 0
    assert capsys.readouterr().out.strip() == "Olá rosto sorridente"


def test_json_spans(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["total:", "12,5", "reais", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["text"] == "total: doze reais e cinquenta centavos"
    assert payload["spans"] == [
        {
            "start": 7,
            "end": 38,
            "original": "12,5 reais",
            "spoken": "doze reais e cinquenta centavos",
            "kind": "money_words",
        }
    ]
    for span in payload["spans"]:
        assert payload["text"][span["start"] : span["end"]] == span["spoken"]


def test_json_spans_multiple_entities(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Paguei", "R$", "5", "em", "05/03/2026", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["text"] == "Paguei cinco reais em cinco de março de dois mil e vinte e seis"
    assert [span["kind"] for span in payload["spans"]] == ["money_symbol", "full_date"]
    for span in payload["spans"]:
        assert payload["text"][span["start"] : span["end"]] == span["spoken"]


def test_ssml_escaping(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["a", "&", "b", "3", "--ssml"]) == 0
    assert capsys.readouterr().out.strip() == (
        '<speak>a e b <say-as interpret-as="cardinal">três</say-as></speak>'
    )


def test_ssml_uses_pipeline_say_as(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["CPF", "123.456.789-09", "--ssml"]) == 0
    output = capsys.readouterr().out.strip()
    assert output.startswith("<speak>")
    assert '<say-as interpret-as="characters">cê pê efe</say-as>' in output
    assert '<say-as interpret-as="digits">' in output
    assert output.endswith("</say-as></speak>")


def test_file_input(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    source = tmp_path / "texto.txt"
    source.write_text("foram 2.000 pessoas", encoding="utf-8")
    assert main(["-f", str(source)]) == 0
    assert capsys.readouterr().out.strip() == "foram dois mil pessoas"


def test_stdin_input(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("século XXI"))
    assert main([]) == 0
    assert capsys.readouterr().out.strip() == "século vinte e um"


def test_unknown_uppercase_token_is_spelled(capsys: pytest.CaptureFixture[str]) -> None:
    """An uppercase token is spelled letter by letter (acronym heuristic)."""
    assert main(["IIII", "e", "5"]) == 0
    assert capsys.readouterr().out.strip() == "i i i i e cinco"


def test_full_entities_from_cli(capsys: pytest.CaptureFixture[str]) -> None:
    """The CLI normalizes every entity class, not only numbers."""
    assert main(["Acesse", "www.exemplo.com", "ou", "joao@example.com"]) == 0
    assert capsys.readouterr().out.strip() == (
        "Acesse w w w ponto exemplo ponto com ou joao arroba example ponto com"
    )


def test_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["texto"])
    assert args.json is False
    assert args.ssml is False
    assert args.decimal_mode == "cardinal"
    assert args.emoji_mode == "remove"
    assert args.roman_context == "cardinal"
    assert args.phone_style == "natural"
    assert args.digit_group_separator == ","
    assert args.acronym_override == []
    assert args.user_lexicon == []
    assert args.max_chars is None


def test_phone_style_option(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Ligue", "(11)", "91234-5678", "--phone-style", "digits"]) == 0
    assert (
        capsys.readouterr().out.strip()
        == "Ligue um um, nove um dois três quatro, cinco seis sete oito"
    )


def test_digit_group_separator_option(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["CPF", "123.456.789-09", "--digit-group-separator", ";"]) == 0
    out = capsys.readouterr().out.strip()
    assert "um dois três; quatro cinco seis; sete oito nove; zero nove" in out


def test_user_lexicon_option(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["O", "INSS", "ligou", "--user-lexicon", "INSS=instituto"]) == 0
    assert capsys.readouterr().out.strip() == "O instituto ligou"


def test_acronym_override_option(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["O", "INSS", "ligou", "--acronym-override", "INSS=word"]) == 0
    assert capsys.readouterr().out.strip() == "O inss ligou"


def test_sentences_and_max_chars(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Um.", "Dois.", "Três.", "--sentences"]) == 0
    assert capsys.readouterr().out.splitlines() == ["Um.", "Dois.", "Três."]
    assert main(["abcdef ghij", "--sentences", "--max-chars", "6"]) == 0
    assert capsys.readouterr().out.splitlines() == ["abcdef", "ghij"]


def test_malformed_pair_flag_is_rejected(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["texto", "--user-lexicon", "SEM_IGUAL"])
    assert exc.value.code == 2
    assert "expects KEY=VALUE" in capsys.readouterr().err
