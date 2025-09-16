# PokeAPI Behave Test Suite

This project demonstrates API automation using **Python + Behave** against the [PokeAPI](https://pokeapi.co).

## Requirements
```bash
pip install -r requirements.txt
```

## Run Tests
Run all scenarios with:
```bash
behave -f pretty
```

Run with JSON report:
```bash
behave -f json -o report.json
```

## Load Testing with Locust
Start locust with:
```bash
locust -f locustfile.py --host https://pokeapi.co
```
Open [http://localhost:8089](http://localhost:8089) to run users.

## Scenarios
- Happy Path (pikachu)
- Boundary IDs (1 and 1026)
- Edge Case (mr-mime)
- Data Validation (schema + mandatory fields)
- Response Headers (Content-Type etc.)

