# Soy Intel — Clean Start

Fresh repo. No patches, no baggage. Backend = FastAPI package. Frontend = premium static SPA.
Use your real files under `data/`.

## Run locally (Firebase Studio or your laptop)
```bash
# If Studio shows "python not installed", install Python 3.12:
# nix profile install nixpkgs#python312   # one-time in Studio

python3 -m venv venv
source venv/bin/activate                  # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python -m svc.main                        # http://localhost:8080/docs
```

Frontend:
```bash
cd frontend
python -m http.server 3000                # http://localhost:3000
```

## Put your data here (rename exactly):
- `data/zl_1d.csv`  (or zl_60.csv, zl_240.csv, zl_1w.csv, zl_1m.csv)  columns: `time,close,...`
- `data/restaurants.csv`  columns: `Name, Casino/Name, Fryers/Count, Active`
- `data/events.jsonl`  each line JSON with `start` or `start_time`, `phq_attendance`, `title/name`, `entities/location`

## Cloud Run deploy
```bash
export PROJECT_ID=us-oil-solutions-app
export REGION=us-central1
bash cloudrun/deploy.sh
```

Point the UI at your API by adding in `frontend/index.html` before scripts:
```html
<script>window.API_BASE='https://YOUR-RUN-URL/api';</script>
```
