"""EJERCICIO 5 — Tu propio tool: calcular_envio
(src/support_agent/tools/calcular_envio.py + tools/__init__.py).

Rojo mientras el handler devuelva el TODO, la descripción/schema estén vacíos
o el tool no esté registrado en TOOLS.
"""

import pytest

from support_agent.agent import run_agent
from support_agent.tools import TOOLS, calcular_envio

pytestmark = pytest.mark.ejercicio


def test_esta_registrado():
    assert "calcular_envio" in TOOLS, "Registra calcular_envio en TOOLS (tools/__init__.py)."


def test_descripcion_util():
    desc = calcular_envio.tool.description
    assert len(desc) >= 60 and "TODO" not in desc, (
        "La descripción es lo que el modelo lee para decidir usar el tool: "
        "di qué hace, cuándo usarlo y qué devuelve."
    )
    assert "env" in desc.lower(), "La descripción debería hablar de envíos."


def test_schema_con_parametros_requeridos():
    schema = calcular_envio.tool.parameters
    props = schema.get("properties", {})
    assert {"canton", "monto_pedido"} <= set(props), (
        "El schema necesita las propiedades canton y monto_pedido."
    )
    assert props["canton"].get("type") == "string"
    assert props["monto_pedido"].get("type") == "integer"
    assert set(schema.get("required", [])) >= {"canton", "monto_pedido"}, (
        "Ambos parámetros deben ser requeridos."
    )
    for nombre in ("canton", "monto_pedido"):
        assert props[nombre].get("description"), f"Describe el parámetro {nombre}."


async def test_handler_zona_gam():
    r = await calcular_envio.handler(canton="Heredia", monto_pedido=10_000)
    assert "error" not in r, r
    assert (r.get("zona"), r.get("costo"), r.get("envio_gratis"), r.get("dias_habiles")) == ("GAM", 1800, False, "1 a 2"), (
        "Heredia es Zona GAM: ₡1.800, 1 a 2 días, sin envío gratis por ₡10.000."
    )


async def test_handler_zona_extendida_con_tilde():
    r = await calcular_envio.handler(canton="Limón", monto_pedido=10_000)
    assert "error" not in r, r
    assert (r.get("zona"), r.get("costo"), r.get("dias_habiles")) == ("Extendida", 3200, "3 a 5"), (
        "Limón es Zona Extendida: ₡3.200 y 3 a 5 días. ¿Normalizas tildes y mayúsculas?"
    )


async def test_handler_envio_gratis():
    r = await calcular_envio.handler(canton="Turrialba", monto_pedido=30_000)
    assert "error" not in r, r
    assert (r.get("zona"), r.get("costo"), r.get("envio_gratis")) == ("Regional", 0, True), (
        "Un pedido de ₡30.000 supera los ₡25.000: el costo debe ser 0 y envio_gratis True."
    )


async def test_handler_canton_desconocido():
    r = await calcular_envio.handler(canton="Atlántida", monto_pedido=5_000)
    assert "error" in r and "Atlántida" in r["error"]


async def test_el_agente_lo_usa():
    result = await run_agent("¿cuánto cuesta el envío a Limón de un pedido de 12000?")
    assert "calcular_envio" in result.tool_calls_made, (
        "El agente debería llamar calcular_envio (con el mock basta que esté registrado)."
    )
    assert "3200" in result.reply
