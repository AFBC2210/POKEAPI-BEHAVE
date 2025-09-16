# Feature: Negative Scenarios - Error Handling in PokeAPI
# Descripción: Este archivo valida cómo la API responde ante solicitudes inválidas, malformadas o potencialmente peligrosas.
# Objetivo: Garantizar que la API maneje correctamente los errores, devuelva mensajes descriptivos y no exponga información sensible.

Feature: Negative Scenarios - Error Handling in PokeAPI
  how the API responds to invalid or malformed requests
 
  # Background: Precondición para todos los escenarios
  # Se verifica que la API esté disponible antes de ejecutar cada prueba.
  Background:
    Given the PokeAPI is available

  # Escenario 1 - 404 Not Found
  # Prueba que la API retorna 404 y un mensaje descriptivo cuando se solicita un Pokémon inexistente.
  Scenario: Pokemon does not exist
    When I request the invalid pokemon id "999999"
    Then the response status code should be 404
    And the error response should contain a descriptive message
    And the response time should be reasonable

  # Escenario 2 - 400 Bad Request
  # Prueba que la API retorna 400 y un mensaje descriptivo ante parámetros malformados en el endpoint de habilidades.
  Scenario: Malformed parameter in ability endpoint
    When I request the ability with invalid id "abc!!"
    Then the response status code should be 400
    And the error response should contain a descriptive message
    And the response time should be reasonable

  # Escenario 3 - 429 Too Many Requests
  # Prueba el mecanismo de rate limiting enviando múltiples solicitudes rápidas y espera un código 429 y mensaje descriptivo.
  Scenario: Rate limiting validation
    When I send multiple rapid requests to "move/1" endpoint
    Then the response status code should be 429
    And the error response should contain a descriptive message

  # Escenario 4 - Timeout Testing
  # Simula una conexión lenta y verifica que la API retorna un timeout después del umbral configurado.
  Scenario: Simulate slow network connection
    When I request the pokemon "ditto" with artificial delay
    Then the response should timeout after the configured threshold

  # Escenario 5 - Parameter Injection
  # Prueba la seguridad ante intentos de inyección de parámetros (SQL Injection) en el endpoint de movimientos.
  # Se espera que la API no retorne 200 ni exponga información sensible.
  Scenario: SQL injection attempt on move endpoint
    When I request the move with invalid id "1; DROP TABLE users;"
    Then the response status code should not be 200
    And the response should not expose sensitive information
