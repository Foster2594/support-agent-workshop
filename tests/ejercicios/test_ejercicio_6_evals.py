"""EJERCICIO 6 — Mini-evals: agrega dos preguntas doradas (evals/preguntas.yaml).

Rojo mientras el set siga teniendo las 11 preguntas originales. Las nuevas
deben estar bien formadas, al menos una debe apuntar a kb/promociones.md, y
el retrieval debe encontrarlas (necesita los Ejercicios 2 y 3 resueltos).
"""

import pytest

from support_agent.evals import load_questions
from support_agent.ingest import ingest_kb
from support_agent.rag import retrieve

pytestmark = pytest.mark.ejercicio

ORIGINALES = 11


def _nuevas() -> list[dict]:
    return load_questions()[ORIGINALES:]


def test_hay_dos_preguntas_nuevas():
    assert len(_nuevas()) >= 2, "Agrega al menos dos preguntas doradas al final del archivo."
    for q in _nuevas():
        assert q.get("pregunta", "").strip(), "Cada entrada necesita 'pregunta'."
        assert str(q.get("fuente_esperada", "")).startswith("kb/"), "fuente_esperada debe ser kb/<archivo>.md"


def test_una_es_de_promociones():
    assert any(q["fuente_esperada"] == "kb/promociones.md" for q in _nuevas()), (
        "Al menos una pregunta nueva debe responderse con kb/promociones.md."
    )


async def test_el_retrieval_las_encuentra():
    assert _nuevas(), "Primero agrega las preguntas nuevas a evals/preguntas.yaml."
    await ingest_kb()
    for q in _nuevas():
        fuentes = [c.source for c in await retrieve(q["pregunta"], top_k=4)]
        assert q["fuente_esperada"] in fuentes, (
            f"{q['pregunta']!r}: {q['fuente_esperada']} no aparece en el top-4 ({fuentes}). "
            "Usa en la pregunta las palabras que aparecen en el documento."
        )
