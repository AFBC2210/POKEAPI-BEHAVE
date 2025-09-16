import os
import requests  # Librería para hacer peticiones HTTP
from behave import given, when, then  # Decoradores para definir pasos de pruebas BDD
from jsonschema import validate, ValidationError  # Validación de esquemas JSON

BASE_URL = os.getenv("POKEAPI_BASE", "https://pokeapi.co")  # URL base de la API, configurable por variable de entorno

POKEMON_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "abilities", "moves", "stats"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "abilities": {"type": "array"},
        "moves": {"type": "array"},
        "stats": {"type": "array"}
    },
    "additionalProperties": True
}  # Esquema para validar la respuesta JSON de un Pokémon

@given('the endpoint "{endpoint}"')
def step_set_endpoint(context, endpoint):
    context.endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"  # Guarda el endpoint para la petición

@when('I send a GET request')
def step_send_get(context):
    url = f"{BASE_URL}{context.endpoint}"
    context.response = requests.get(url, timeout=8)  # Realiza la petición GET
    try:
        context.json = context.response.json()  # Intenta obtener el JSON de la respuesta
    except ValueError:
        context.json = None  # Si falla, asigna None

@then('the response status should be {expected_status:d}')
def step_check_status(context, expected_status):
    actual = context.response.status_code
    assert actual == expected_status, f"Expected {expected_status}, got {actual}"  # Verifica el código de estado

@then('the response time should be less than {seconds:d} seconds')
def step_check_time(context, seconds):
    elapsed = context.response.elapsed.total_seconds()
    assert elapsed < seconds, f"Response time {elapsed}s exceeds {seconds}s"  # Verifica el tiempo de respuesta

@then('the response Content-Type should contain "{mime}"')
def step_check_content_type(context, mime):
    ct = context.response.headers.get("Content-Type", "")
    assert mime in ct, f"Content-Type missing or not containing '{mime}': {ct}"  # Verifica el tipo de contenido

@then('the JSON must contain keys "{keys}"')
def step_check_keys(context, keys):
    assert context.json is not None, "Response is not valid JSON"
    required = [k.strip() for k in keys.split(",")]
    for k in required:
        assert k in context.json, f"Missing key: {k}"  # Verifica que existan las claves requeridas

@then('the response should validate against the Pokemon JSON schema')
def step_validate_schema(context):
    assert context.json is not None, "Response is not valid JSON"
    try:
        validate(instance=context.json, schema=POKEMON_SCHEMA)  # Valida el JSON contra el esquema
    except ValidationError as e:
        raise AssertionError(f"JSON schema validation failed: {e.message}")
