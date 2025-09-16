"""
Este archivo contiene los pasos de Behave para validar escenarios negativos y manejo de errores en la PokeAPI.

"""

import requests
import time
from behave import when, then, given

BASE_URL = "https://pokeapi.co/api/v2"

@given('the PokeAPI is available')
def step_impl(context):
    """
    Verifica que la PokeAPI esté disponible antes de ejecutar los escenarios.
    Realiza una petición simple al endpoint base y valida el status.
    """
    url = f"{BASE_URL}/pokemon/1"
    resp = requests.get(url)
    assert resp.status_code == 200, f"PokeAPI is not available, status: {resp.status_code}"


# --- Escenario 1: 404 Not Found ---
@when('I request the invalid pokemon id "{invalid_id}"')
def step_impl(context, invalid_id):
    """
    Solicita un Pokémon con un ID inválido para probar el manejo de errores 404.
    Guarda el tiempo de respuesta y la respuesta HTTP en el contexto.
    """
    url = f"{BASE_URL}/pokemon/{invalid_id}"
    context.start_time = time.time()
    context.response = requests.get(url)
    context.elapsed_time = time.time() - context.start_time

@then('the error response should contain a descriptive message')
def step_impl(context):
    """
    Verifica que la respuesta de error contenga un mensaje descriptivo o el código esperado.
    """
    json_data = {}
    try:
        json_data = context.response.json()
    except Exception:
        pass  # algunos errores pueden no traer JSON
    assert "error" in str(json_data).lower() or context.response.status_code in [404, 400, 429]

@then('the response time should be reasonable')
def step_impl(context):
    """
    Verifica que el tiempo de respuesta sea menor a 3 segundos.
    """
    assert context.elapsed_time < 3, f"Response too slow: {context.elapsed_time}s"


# --- Escenario 2: 400 Bad Request ---
@when('I request the ability with invalid id "{invalid_id}"')
def step_impl(context, invalid_id):
    """
    Solicita una habilidad con un ID inválido para probar el manejo de errores 400.
    Guarda el tiempo de respuesta y la respuesta HTTP en el contexto.
    """
    url = f"{BASE_URL}/ability/{invalid_id}"
    context.start_time = time.time()
    context.response = requests.get(url)
    context.elapsed_time = time.time() - context.start_time


# --- Escenario 3: 429 Too Many Requests ---
@when('I send multiple rapid requests to "{endpoint}" endpoint')
def step_impl(context, endpoint):
    """
    Envía múltiples solicitudes rápidas al endpoint para probar el rate limiting (429).
    Guarda la última respuesta HTTP en el contexto.
    """
    url = f"{BASE_URL}/{endpoint}"
    last_resp = None
    for _ in range(10):  # bombardear con requests
        resp = requests.get(url)
        last_resp = resp
        if resp.status_code == 429:
            context.response = resp
            return
    context.response = last_resp  # Siempre guarda el objeto Response


# --- Escenario 4: Timeout Testing ---
@when('I request the pokemon "{pokemon_name}" with artificial delay')
def step_impl(context, pokemon_name):
    """
    Solicita un Pokémon con un timeout artificialmente bajo para probar el manejo de timeouts.
    Guarda la respuesta HTTP en el contexto, o None si ocurre timeout.
    """
    url = f"{BASE_URL}/pokemon/{pokemon_name}"
    try:
        # Forzar timeout bajo (ej. 0.001s)
        context.response = requests.get(url, timeout=0.001)
    except requests.exceptions.Timeout:
        context.response = None  # Marca que fue timeout


@then('the response should timeout after the configured threshold')
def step_impl(context):
    """
    Verifica que la respuesta sea None, indicando que ocurrió un timeout.
    """
    assert context.response is None, "Expected request to timeout but it completed"


# --- Escenario 5: Parameter Injection ---
@when('I request the move with invalid id "{invalid_id}"')
def step_impl(context, invalid_id):
    """
    Solicita el endpoint de movimientos con un ID malicioso para probar inyección de parámetros.
    Guarda la respuesta HTTP en el contexto.
    """
    url = f"{BASE_URL}/move/{invalid_id}"
    context.response = requests.get(url)

@then('the response should not expose sensitive information')
def step_impl(context):
    """
    Verifica que la respuesta no exponga detalles sensibles como errores SQL o excepciones.
    """
    body = context.response.text.lower()
    assert "sql" not in body and "exception" not in body, \
        "Response exposed sensitive error details"


# --- Steps para status code ---
@then('the response status code should be 404')
def step_impl(context):
    """
    Verifica que el código de estado HTTP sea 404.
    """
    assert context.response.status_code == 404, f"Expected 404, got {context.response.status_code}"

@then('the response status code should be 400')
def step_impl(context):
    """
    Verifica que el código de estado HTTP sea 400.
    """
    assert context.response.status_code == 400, f"Expected 400, got {context.response.status_code}"

@then('the response status code should be 429')
def step_impl(context):
    """
    Verifica que el código de estado HTTP sea 429.
    """
    assert context.response.status_code == 429, f"Expected 429, got {context.response.status_code}"

@then('the response status code should not be 200')
def step_impl(context):
    """
    Verifica que el código de estado HTTP no sea 200.
    """
    assert context.response.status_code != 200, f"Expected not 200, got {context.response.status_code}"
