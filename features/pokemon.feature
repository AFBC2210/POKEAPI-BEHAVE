# Feature: Pruebas para el endpoint GET /pokemon/{pokemon}
# Este archivo define escenarios para validar la API de Pokémon.
Feature: Pokemon API - GET /pokemon/{pokemon}
  Ensure the Pokemon endpoint returns correct status, headers, timing and JSON structure.

  # Escenario feliz: consulta por nombre válido
  Scenario: Happy Path - valid pokemon name
    Given the endpoint "/api/v2/pokemon/pikachu"
    When I send a GET request
    Then the response status should be 200
    And the response time should be less than 2 seconds
    And the response Content-Type should contain "application/json"
    And the JSON must contain keys "id, name, abilities, moves, stats"

  # Escenario Alterno valido: consulta por ID válido
  Scenario: Boundary - valid ID = 1
    Given the endpoint "/api/v2/pokemon/1"
    When I send a GET request
    Then the response status should be 200
    And the response time should be less than 2 seconds
    And the JSON must contain keys "id, name, abilities, moves, stats"

  # Escenario Alterno invalido: consulta por ID inválido
  Scenario: Boundary - invalid ID >= 101010
    Given the endpoint "/api/v2/pokemon/101010"
    When I send a GET request
    Then the response status should be 404
    And the response time should be less than 2 seconds

  # Escenario caracteres especiales: nombre con caracteres especiales
  Scenario: Edge Case - name with special characters
    Given the endpoint "/api/v2/pokemon/mr-mime"
    When I send a GET request
    Then the response status should be 200
    And the response time should be less than 2 seconds
    And the JSON must contain keys "id, name, abilities, moves, stats"

  # Validación de datos y cabeceras
  Scenario: Data Validation and Response Headers
    Given the endpoint "/api/v2/pokemon/pikachu"
    When I send a GET request
    Then the response status should be 200
    And the response Content-Type should contain "application/json"
    And the response should validate against the Pokemon JSON schema
