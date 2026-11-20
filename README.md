# Data pipeline engineering blog post

This package contains the article project JSON, its generated page and the unchanged JSON page generator.

## View

Open `output/data-pipeline-engineering/index.html`. Keep its `assets/` folder alongside it. Publish the entire output folder to your static hosting service.

## Edit and regenerate

All content, navigation and layout live in `input/data-pipeline-engineering/page.json`. Page metadata and theme overrides live in `site.json`. The selected project is set in `input/config.json`.

From this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r generator/requirements.txt
python generator/main.py
```

To deploy the index to the localhost:
```
python -m http.server 8000 --bind 127.0.0.1
```

To use your existing generator instead, copy `input/data-pipeline-engineering/` into its `input/` folder and set `project` to `data-pipeline-engineering`.

The article wording, heading hierarchy, lists and inline emphasis are preserved from the supplied DOCX. Navigation, author identification, cover and estimated reading time were added for the blog layout. No new technical claims or references were added. External web fonts require internet access. The cover image is included locally.
