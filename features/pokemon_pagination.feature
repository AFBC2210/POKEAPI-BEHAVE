# Feature: Pruebas de paginación para el endpoint GET /pokemon
# Este archivo valida la paginación, metadatos, navegación y consistencia de datos en la API de Pokémon.
Feature: Pokemon API Pagination - GET /pokemon?limit={limit}&offset={offset}
  Validate list pagination, metadata, navigation and data consistency.

  # Configuración inicial para todos los escenarios
  Background:
    Given the PokeAPI base URL is configured

  # Escenario: El límite por defecto es 20 si no se especifica
  Scenario: Default limit is 20 when no limit provided
    When I request the pokemon list without limit and offset
    Then the pagination response status should be exactly 200
    And the number of results returned should be 20

  # Escenario: El límite puede configurarse y nunca excede el valor dado
  Scenario Outline: Configurable limits produce at most <limit> results
    When I request the pokemon list with limit <limit> and offset 0
    Then the pagination response status should be exactly 200
    And the number of results returned should be less than or equal to <limit>

    Examples:
      | limit |
      | 1     |
      | 50    |
      | 100   |
      | 1000  |

  # Escenario: Navegación entre páginas y consistencia de datos
  Scenario: Normal pagination and bidirectional navigation (limit=20)
    Given I request the list with limit 20 and offset 0
    And I request the list with limit 20 and offset 20
    And I request the list with limit 20 and offset 40
    Then next and previous links should be valid where applicable
    And there should be no duplicate pokemon between those pages
    And the metadata count should be consistent across these pages

  # Escenario: Offset fuera de rango retorna resultados vacíos o sanitizados
  Scenario: Offset out of range returns empty results (or sanitized response)
    Given I get the total count from the service
    When I request the list with limit 20 and offset greater than count + 1000
    Then the pagination response status should be exactly 200
    And the results list should be empty

  # Escenario: Parámetros negativos se manejan correctamente
  Scenario: Negative parameters handled gracefully
    When I request the list with limit -1 and offset -10
    Then the service should either return an error (status >= 400) or return a sanitized response (status 200 with valid results)
    # Se acepta cualquier comportamiento documentado, pero se registra cuál ocurre

  # Escenario: Consistencia temporal, la misma página retorna los mismos datos en el tiempo
  Scenario: Consistency temporal - same page returns same items across time
    Given I request the list with limit 20 and offset 40 and capture the names
    When I wait 2 seconds and request the same list again
    Then the names returned should be identical (order and items)
