
"""
Modelo de Pokémon usado en pruebas de paginación.

Este archivo define la clase Pokemon, que representa un elemento básico de la lista de resultados de la API.
Permite cargar detalles adicionales desde la URL y validar la estructura mínima esperada.

Buenas prácticas:
- Clase pequeña y de única responsabilidad.
- Docstrings claros y type hints.
- Separación de lógica de red y validación.
"""

from typing import List
import requests  # Usado para obtener detalles del Pokémon desde la API

class Pokemon:
    def __init__(self, name: str, url: str):
        """
        Inicializa el modelo básico de Pokémon para la lista de resultados.
        :param name: nombre del Pokémon (string)
        :param url: enlace al recurso de detalles del Pokémon (string)
        """
        self.name: str = name  # Nombre del Pokémon
        self.url: str = url  # URL al detalle del Pokémon
        self.abilities: List[dict] = []  # Lista de habilidades
        self.moves: List[dict] = []      # Lista de movimientos
        self.stats: List[dict] = []      # Lista de estadísticas

    def load_details(self, timeout: int = 8) -> None:
        """
        Obtiene el recurso de detalle y llena las listas de habilidades, movimientos y estadísticas.
        No lanza excepción si falla, el manejo queda a cargo del llamador.
        """
        if not self.url:
            return
        resp = requests.get(self.url, timeout=timeout)
        if resp.status_code != 200:
            # No se lanza excepción aquí — el llamador decide cómo manejar fallos.
            return
        data = resp.json()
        # Extracción defensiva con listas vacías por defecto
        self.abilities = data.get("abilities", [])
        self.moves = data.get("moves", [])
        self.stats = data.get("stats", [])

    def validate_structure(self) -> bool:
        """
        Valida la estructura mínima esperada para un elemento de la lista:
        - name debe ser un string no vacío
        - url debe ser un string no vacío y parecer una URL http(s)
        - abilities/moves/stats deben ser listas (pueden estar vacías)
        Retorna True si es válido, False si no.
        """
        if not isinstance(self.name, str) or not self.name.strip():
            return False
        if not isinstance(self.url, str) or not self.url.strip():
            return False
        # Verificación simple de URL
        if not (self.url.startswith("http://") or self.url.startswith("https://")):
            return False
        if not isinstance(self.abilities, list) or not isinstance(self.moves, list) or not isinstance(self.stats, list):
            return False
        return True
