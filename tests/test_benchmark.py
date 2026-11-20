"""Throughput benchmark for the composed normalization pipeline.

The SPEC target is 100k words/s.  The assertion below is deliberately generous
(a 5x margin) so it catches a real performance regression without flaking on a
slow CI runner; run ``pytest -s`` to see the measured rate.
"""

from __future__ import annotations

import re
import time

from falabr import normalize

_BENCH_TEXT: str = (
    "A Petrobras anunciou hoje que investiu R$ 2,5 bi em projetos. "
    "A empresa emprega 45 mil pessoas. Segundo o IBGE, a inflação ficou em 3,14% no ano. "
    "CPF 123.456.789-09. Tel. (11) 91234-5678. "
)
_REPEAT: int = 1000
_MIN_WORDS_PER_SECOND: int = 20_000


def test_throughput_benchmark() -> None:
    text = _BENCH_TEXT * _REPEAT
    word_count = len(_BENCH_TEXT.split()) * _REPEAT

    start = time.perf_counter()
    output = normalize(text)
    elapsed = time.perf_counter() - start

    assert elapsed > 0
    rate = word_count / elapsed
    assert rate >= _MIN_WORDS_PER_SECOND, f"throughput too low: {rate:.0f} words/s"
    # Correctness under load: every number in the corpus must have been spoken.
    assert output
    assert not re.search(r"\d", output)
