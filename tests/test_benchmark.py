"""Throughput benchmark for the composed normalization pipeline.

The SPEC target is 100k words/s.  The assertion below is deliberately generous
(a 5x margin) so it catches a real performance regression without flaking on a
slow CI runner; run ``pytest -s`` to see the measured rate.
"""

from __future__ import annotations

import re
import sys
import time

from falabr import normalize

_BENCH_TEXT: str = (
    "A Petrobras anunciou hoje que investiu R$ 2,5 bi em projetos. "
    "A empresa emprega 45 mil pessoas. Segundo o IBGE, a inflação ficou em 3,14% no ano. "
    "CPF 123.456.789-09. Tel. (11) 91234-5678. "
)
_REPEAT: int = 1000
_MIN_WORDS_PER_SECOND: int = 20_000
# CI runs the suite under ``coverage run``, whose line tracer slows pure-Python
# code by roughly 5x (measured: ~100k words/s untraced vs ~20k traced on a
# macOS runner). The bound is scaled when a tracer is active so the benchmark
# still flags real regressions instead of measuring the instrumentation.
_TRACER_SLOWDOWN: int = 5
_RUNS: int = 3


def test_throughput_benchmark() -> None:
    text = _BENCH_TEXT * _REPEAT
    word_count = len(_BENCH_TEXT.split()) * _REPEAT

    best_rate = 0.0
    output = ""
    for _ in range(_RUNS):
        start = time.perf_counter()
        output = normalize(text)
        elapsed = time.perf_counter() - start
        assert elapsed > 0
        best_rate = max(best_rate, word_count / elapsed)

    minimum = _MIN_WORDS_PER_SECOND
    if sys.gettrace() is not None:
        minimum //= _TRACER_SLOWDOWN
    assert best_rate >= minimum, f"throughput too low: {best_rate:.0f} words/s (min {minimum})"
    # Correctness under load: every number in the corpus must have been spoken.
    assert output
    assert not re.search(r"\d", output)
