Set-Location $PSScriptRoot
python -m uvicorn femcycle_companion.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir femcycle_companion --reload-dir templates --reload-dir static

