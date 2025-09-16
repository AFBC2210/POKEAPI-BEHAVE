# Feature: Security and Observability for PokeAPI
# Descripción: Este archivo valida prácticas de seguridad y señales de observabilidad en la API de Pokémon.
# Objetivo: Garantizar que la API sea robusta ante ataques y proporcione métricas operacionales útiles.

Feature: Security and Observability for PokeAPI
  validate security practices and observability signals
  So that the API is robust against attacks and provides operational insights

  # Escenario: Sanitización de entradas contra payloads maliciosos
  # Prueba que la API no retorne errores 500 ni información sensible ante entradas maliciosas.
  @security @injection
  Scenario Outline: Input sanitization against malicious payloads
    When I send a GET request to "<endpoint>" with malicious payload "<payload>"
    Then the response code should not be 500
    And the response should not contain sensitive information

    Examples:
      | endpoint          | payload        |
      | pokemon           | ' OR '1'='1   |
      | ability           | <script>test  |
      | move              | DROP TABLE    |

  # Escenario: Rate limiting
  # Prueba que la API limite el número de peticiones y retorne 429 si se excede el umbral.
  @security @ratelimit
  Scenario: Validate rate limiting with multiple requests
    When I send 50 rapid GET requests to "pokemon/pikachu"
    Then at least one response code should be 429

  # Escenario: Encabezados de seguridad en respuestas de error
  # Valida que la API incluya encabezados de seguridad en respuestas de error.
  @security @headers
  Scenario: Validate security headers in error responses
    When I send a GET request to "pokemon/invalid_id"
    Then the response headers should include "X-Frame-Options"
    And the response headers should include "Access-Control-Allow-Origin"

  # Escenario: Logging estructurado con IDs de correlación
  # Prueba que la API incluya el header de correlación en la respuesta para trazabilidad.
  @observability @logging
  Scenario: Structured logging with correlation IDs
    When I send a GET request to "pokemon/pikachu" with header "X-Correlation-ID: test-123"
    Then the response headers should include "X-Correlation-ID"

  # Escenario: Métricas de cobertura de endpoints
  # Valida que la API reporte métricas de cobertura de pruebas sobre los endpoints.
  @observability @metrics
  Scenario: Endpoint coverage tracking
    Given I have executed tests for multiple endpoints
    When I calculate endpoint coverage
    Then the coverage percentage should be greater than 80

  # Escenario: Alertas automáticas ante degradación de rendimiento
  # Prueba que la API genere alertas ante respuestas lentas.
  @observability @alerts
  Scenario: Automatic alerts on performance degradation
    When I simulate a slow response from "pokemon/ditto"
    Then an alert should be triggered for performance degradation
