# document-search
Service for document search and RAG for Nornickel case on AI Product Hack 2024

## Структура

- `document_search/`
    - `ocr/` - все что нужно для ocr документов
    - `search/` - embedder, retrieval и все что нужно для построения индекса
    - `storages/` - хранилища
    - `entities.py` - структуры для обработанных документов и сущностей

## Установка

Необходим python версиии >=3.10

```bash
git clone https://github.com/boomb0om/document-search
cd document-search
pip install .
```

### Локальная разработка

Установка для локальной разработки:

```bash
git clone https://github.com/boomb0om/document-search
cd document-search
pip install ".[dev]"
```

Также установите make.

Чтобы запустить проверку кодстайла, выполните: `make codestyle`. Чтобы запустить автоматический фикс кодстайла, выполните: `make autofix`