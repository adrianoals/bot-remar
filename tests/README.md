# Testes

## Estrutura

- `unit/`: testes de logica com mocks
- `contracts/`: contratos de payload/eventos esperados
- `integration/`: testes reais opcionais (servicos externos)
- `fixtures/`: payloads de referencia

## Execucao

Todos os testes automatizados (exceto live, que ficam skip por padrao):

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Executar testes de integracao reais com Supabase:

```bash
RUN_LIVE_TESTS=1 python -m unittest discover -s tests/integration -p "test_*.py" -v
```
