
"""
pruebas de paginación en la API de Pokémon.

Este archivo contiene las definiciones de los pasos para validar la paginación, metadatos, navegación y consistencia 
de datos en la API de Pokémon.

"""

import time
from urllib.parse import urlparse, parse_qs
import requests  # Usado para hacer peticiones HTTP
from behave import given, when, then
from features.support.pokemon_model import Pokemon

DEFAULT_TIMEOUT = 8
DEFAULT_LIMIT = 20  # Límite por defecto esperado

# Función auxiliar para obtener la lista de Pokémon
# Permite parametrizar limit y offset, y retorna la respuesta y el JSON

def _get_list(limit=None, offset=None, base_url="https://pokeapi.co/api/v2"):
    """
    Solicita el recurso y retorna (response, json_data)
    :param limit: cantidad máxima de resultados
    :param offset: desplazamiento en la lista
    :param base_url: URL base de la API
    """
    url = f"{base_url}/pokemon"
    params = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
    try:
        json_data = resp.json()
    except ValueError:
        json_data = None
    return resp, json_data

@given('the PokeAPI base URL is configured')
def step_base_url(context):
    """
    Configura la URL base en el contexto de Behave.
    """
    context.base_url = getattr(context, "base_url", "https://pokeapi.co/api/v2")

@when('I request the pokemon list without limit and offset')
def step_request_default(context):
    """
    Solicita la lista de Pokémon sin parámetros de paginación.
    """
    context.resp, context.json = _get_list(base_url=context.base_url)

@when('I request the pokemon list with limit {limit:d} and offset {offset:d}')
def step_request_with_params(context, limit, offset):
    """
    Solicita la lista de Pokémon con limit y offset.
    """
    context.resp, context.json = _get_list(limit=limit, offset=offset, base_url=context.base_url)

@when('I request the pokemon list with limit {limit:d} and offset 0')
def step_request_limit(context, limit):
    """
    Solicita la lista de Pokémon con limit y offset=0.
    """
    context.resp, context.json = _get_list(limit=limit, offset=0, base_url=context.base_url)

@when('I request the list with limit {limit:d} and offset {offset:d}')
def step_request_list(context, limit, offset):
    """
    Solicita la lista de Pokémon con limit y offset (nombres alternativos para claridad).
    """
    context.resp, context.json = _get_list(limit=limit, offset=offset, base_url=context.base_url)

@given('I request the list with limit 20 and offset 0')
def step_request_offset_0(context):
    """
    Solicita la lista con limit=20 y offset=0 y la guarda en context.pages.
    """
    context.resp, context.json = _get_list(limit=20, offset=0, base_url=context.base_url)
    if not hasattr(context, "pages"): context.pages = []
    context.pages.append({"offset": 0, "resp": context.resp, "json": context.json})

@given('I request the list with limit 20 and offset 20')
def step_request_offset_20(context):
    """
    Solicita la lista con limit=20 y offset=20 y la guarda en context.pages.
    """
    context.resp, context.json = _get_list(limit=20, offset=20, base_url=context.base_url)
    if not hasattr(context, "pages"): context.pages = []
    context.pages.append({"offset": 20, "resp": context.resp, "json": context.json})

@given('I request the list with limit 20 and offset 40')
def step_request_offset_40(context):
    """
    Solicita la lista con limit=20 y offset=40 y la guarda en context.pages.
    """
    context.resp, context.json = _get_list(limit=20, offset=40, base_url=context.base_url)
    if not hasattr(context, "pages"): context.pages = []
    context.pages.append({"offset": 40, "resp": context.resp, "json": context.json})

@given('I get the total count from the service')
def step_get_count(context):
    """
    Obtiene el total de Pokémon disponibles en la API y lo guarda en context.total_count.
    """
    resp, json_data = _get_list(limit=1, offset=0, base_url=context.base_url)
    assert resp.status_code == 200, f"Cannot obtain count, status={resp.status_code}"
    context.total_count = json_data.get("count")
    assert isinstance(context.total_count, int) and context.total_count > 0, "Invalid count value"

@when('I request the list with limit 20 and offset greater than count + 1000')
def step_request_offset_out_of_range(context):
    """
    Solicita la lista con un offset fuera de rango para probar la respuesta vacía.
    """
    offset = context.total_count + 1000
    context.resp, context.json = _get_list(limit=20, offset=offset, base_url=context.base_url)

@then('the pagination response status should be {expected_status:d}')
def step_check_status(context, expected_status):
    """
    Verifica el código de estado HTTP de la respuesta.
    """
    actual = context.resp.status_code
    assert actual == expected_status, f"Expected status {expected_status}, got {actual}"

@then('the number of results returned should be {expected:d}')
def step_check_results_count_equal(context, expected):
    """
    Verifica que la cantidad de resultados sea exactamente la esperada.
    """
    results = context.json.get("results", []) if context.json else []
    assert isinstance(results, list), "Results is not a list"
    actual = len(results)
    assert actual == expected, f"Expected {expected} results, got {actual}"

@then('the number of results returned should be less than or equal to {limit:d}')
def step_check_results_le(context, limit):
    """
    Verifica que la cantidad de resultados no exceda el límite dado.
    """
    results = context.json.get("results", []) if context.json else []
    assert len(results) <= limit, f"Results length {len(results)} > {limit}"

@then('next and previous links should be valid where applicable')
def step_check_next_prev(context):
    """
    Verifica que los enlaces next/previous sean URLs válidas y accesibles.
    """
    for page in getattr(context, "pages", []):
        json_data = page["json"]
        if not json_data:
            continue
        for link_key in ("next", "previous"):
            link = json_data.get(link_key)
            if link:
                parsed = urlparse(link)
                assert parsed.scheme in ("http", "https"), f"{link_key} is not a valid URL: {link}"
                r = requests.get(link, timeout=DEFAULT_TIMEOUT)
                assert r.status_code == 200, f"{link_key} URL returned {r.status_code}: {link}"

@then('there should be no duplicate pokemon between those pages')
def step_check_no_duplicates(context):
    """
    Verifica que no haya nombres duplicados entre páginas de resultados.
    """
    seen = set()
    duplicates = []
    for page in getattr(context, "pages", []):
        json_results = page["json"].get("results", []) if page["json"] else []
        for item in json_results:
            name = item.get("name")
            if name in seen:
                duplicates.append(name)
            else:
                seen.add(name)
    assert not duplicates, f"Found duplicate names across pages: {duplicates}"

@then('the metadata count should be consistent across these pages')
def step_check_metadata_count_consistency(context):
    """
    Verifica que el valor de count sea consistente entre todas las páginas consultadas.
    """
    counts = []
    for page in getattr(context, "pages", []):
        json_data = page["json"]
        if not json_data:
            continue
        counts.append(json_data.get("count"))
    unique_counts = set(c for c in counts if c is not None)
    assert len(unique_counts) <= 1, f"Inconsistent count values across pages: {unique_counts}"
    if unique_counts:
        context.total_count = unique_counts.pop()

@then('the results list should be empty')
def step_check_empty_results(context):
    """
    Verifica que la lista de resultados esté vacía.
    """
    results = context.json.get("results", []) if context.json else []
    assert len(results) == 0, f"Expected empty results, got {len(results)}"

@then('the pagination response status should be exactly 200')
def step_check_status_200(context):
    """
    Verifica que el código de estado HTTP sea exactamente 200.
    """
    actual = context.resp.status_code
    assert actual == 200, f"Expected status 200, got {actual}"

@then('the service should either return an error (status >= 400) or return a sanitized response (status 200 with valid results)')
def step_check_negative_params_behavior(context):
    """
    Verifica que el servicio maneje parámetros negativos correctamente, aceptando error o respuesta sanitizada.
    """
    status = context.resp.status_code
    if status >= 400:
        print(f"Service returned error status {status} for negative params (acceptable).")
        return
    json_data = context.json or {}
    results = json_data.get("results", [])
    assert isinstance(results, list), "Sanitized response results is not a list"
    assert 0 <= len(results) <= 1000, f"Sanitized results length unexpected: {len(results)}"

@given('I request the list with limit 20 and offset 40 and capture the names')
def step_capture_names_given(context):
    """
    Solicita la lista con limit=20 y offset=40, guarda los nombres para comparar consistencia temporal.
    """
    resp, json_data = _get_list(limit=20, offset=40, base_url=context.base_url)
    assert resp.status_code == 200, f"Failed to fetch page for consistency check, status {resp.status_code}"
    results = json_data.get("results", [])
    names = [r.get("name") for r in results]
    context.captured_names = names
    context.last_offset = 40

@when('I wait {seconds:d} seconds and request the same list again')
def step_wait_and_request_again(context, seconds):
    """
    Espera y vuelve a solicitar la misma página para comparar resultados y consistencia temporal.
    """
    time.sleep(seconds)
    offset = context.last_offset if hasattr(context, "last_offset") else 40
    context.resp_second, context.json_second = _get_list(limit=20, offset=offset, base_url=context.base_url)

@then('the names returned should be identical (order and items)')
def step_assert_names_identical(context):
    """
    Compara que los nombres capturados sean idénticos en orden y contenido entre dos consultas.
    """
    names1 = context.captured_names
    names2 = [r.get("name") for r in (context.json_second.get("results", []) if context.json_second else [])]
    assert names1 == names2, f"Lists differ. first: {names1[:5]}..., second: {names2[:5]}..."
