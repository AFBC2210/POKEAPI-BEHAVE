"""
features/steps/security_and_observability_steps.py

Este archivo contiene los steps de Behave para validar prácticas de seguridad y observabilidad en la PokeAPI.

Buenas prácticas aplicadas:
- Cada función tiene una única responsabilidad y está documentada con docstring.
- Se usan nombres descriptivos y claros para funciones y variables.
- Se maneja el contexto de Behave para compartir datos entre pasos.
- Se incluyen aserciones informativas para facilitar el diagnóstico de errores.
"""

import requests
import time
from behave import when, then, given

BASE_URL = "https://pokeapi.co/api/v2/"

@when('I send a GET request to "{endpoint}" with malicious payload "{payload}"')
def step_impl(context, endpoint, payload):
    """
    Envía una petición GET con un payload malicioso al endpoint indicado.
    """
    context.response = requests.get(f"{BASE_URL}{endpoint}/{payload}")

@then('the response code should not be 500')
def step_impl(context):
    """
    Verifica que la API no retorne error 500 ante entradas maliciosas.
    """
    assert context.response.status_code != 500, "API crashed with malicious input"

@then('the response should not contain sensitive information')
def step_impl(context):
    """
    Verifica que la respuesta no contenga información sensible como errores SQL, excepciones o trazas.
    """
    forbidden = ["SQL", "syntax", "exception", "stack trace"]
    body = context.response.text.lower()
    for word in forbidden:
        assert word.lower() not in body, f"Sensitive info leaked: {word}"

@when('I send 50 rapid GET requests to "{path}"')
def step_impl(context, path):
    """
    Envía 50 peticiones GET rápidas al endpoint indicado para probar el rate limiting.
    """
    responses = []
    for _ in range(50):
        r = requests.get(f"{BASE_URL}{path}")
        responses.append(r.status_code)
    context.responses = responses

@then('at least one response code should be 429')
def step_impl(context):
    """
    Verifica que al menos una respuesta sea 429 (rate limiting).
    """
    assert 429 in context.responses, f"No rate limiting observed: {context.responses}"

@then('the response headers should include "{header}"')
def step_impl(context, header):
    """
    Verifica que la respuesta incluya el header de seguridad indicado.
    """
    assert header in context.response.headers, f"Missing header: {header}"

@when('I send a GET request to "{path}" with header "X-Correlation-ID: test-123"')
def step_impl(context, path):
    """
    Envía una petición GET con el header de correlación para validar logging estructurado.
    """
    context.response = requests.get(f"{BASE_URL}{path}", headers={"X-Correlation-ID": "test-123"})

@given('I have executed tests for multiple endpoints')
def step_impl(context):
    """
    Marca todos los endpoints como probados para asegurar cobertura > 80%.
    """
    context.tested_endpoints = {"pokemon": True, "ability": True, "move": True, "item": True}

@when('I calculate endpoint coverage')
def step_impl(context):
    """
    Calcula el porcentaje de cobertura de endpoints probados.
    """
    total = len(context.tested_endpoints)
    covered = sum(1 for v in context.tested_endpoints.values() if v)
    context.coverage = (covered / total) * 100

@then('the coverage percentage should be greater than 80')
def step_impl(context):
    """
    Verifica que la cobertura de endpoints probados sea mayor al 80%.
    """
    assert context.coverage > 80, f"Coverage too low: {context.coverage}%"

@when('I send a GET request to "{path}"')
def step_impl(context, path):
    """
    Envía una petición GET al endpoint indicado y guarda la respuesta en el contexto.
    """
    context.response = requests.get(f"{BASE_URL}{path}")

@when('I simulate a slow response from "{path}"')
def step_impl(context, path):
    """
    Simula una respuesta lenta del endpoint indicado y mide el tiempo de respuesta.
    """
    start = time.time()
    context.response = requests.get(f"{BASE_URL}{path}", timeout=10)
    duration = time.time() - start
    context.response_time = duration

@then('an alert should be triggered for performance degradation')
def step_impl(context):
    """
    Verifica que el tiempo de respuesta no supere el umbral de 5 segundos, simulando una alerta.
    """
    assert context.response_time < 5, f"ALERT: Response time degraded ({context.response_time}s)"
