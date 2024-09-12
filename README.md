# document-search
Сервис для поиска и RAG по базе нормативных документов для кейса Норникеля на AI Product Hack 2024.

## Структура

- `frontend/` - фронтенд
- `main.py` - бэкенд
- `document_search/`
    - `ocr/` - все что нужно для ocr документов
    - `search/` - embedder и все что нужно для построения индекса
    - `rag/` - retrieval и реализация RAG
    - `storages/` - хранилища
    - `entities.py` - структуры для обработанных документов и сущностей
    - `types.py` - кастомные аннотации типов
    - `utils.py` - утилиты
- `notebooks/` - jupyter notebooks с примерами

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

## Запуск проекта

Посмотреть примеры и запустить каждый из компонент отдельно можно в ноутбуках в папке `notebooks/`.

### Запуск backend

В файле `document_search/rag/credentials.py` введите ваши креды к YandexGPT API, чтобы была возможность использовать RAG.

Запустите бэкенд:
```python
python main.py --port=8080
```

### Запуск frontend-части

Для запуска необходимо определить переменную окружения `BACKEND_API_URL`, в которой должен лежать путь к API бэкенда, например `export BACKEND_API_URL=http://localhost:8080`.

Затем выполните команду:
```bash
streamlit run frontend/main.py --server.port=<your-frontend-port>
```

## TODO

- [ ] Добавить поддержку различных форматов документов (txt, md, xml, docx)
- [ ] Добавить другие модели для кодирования текста в эмбеддинг (сейчас только `intfloat/multilingual-e5-base`)
- [ ] Добавить переформулирование запроса пользователя с помощью LLM и одновременный поиск по всем этим запросам
- [ ] Добавить поиск алгоритмом BM25 
- [ ] Оптимизировать выбор контекста для подачи в RAG

## Коллектив авторов
- Игорь Павлов [github](https://github.com/boomb0om)
- Артем Иванов [github](https://github.com/UsefulTornado)
- Станислав Стафиевский [github](https://github.com/stasstaf)
- Анастасия Остапчук [github](https://github.com/aniciya777)
