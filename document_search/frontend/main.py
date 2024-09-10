import logging
import time

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from document_search.frontend.api import (
    add_document,
    get_storage_info,
    get_uploading_status,
    search_query,
)


def get_doc_id2filename() -> dict[str, str]:
    storage_info = get_storage_info()
    return {
        item["document_id"]: item["document_filename"] for item in storage_info["items"]
    }


def get_doc_filename2id() -> dict[str, str]:
    storage_info = get_storage_info()
    return {
        item["document_filename"]: item["document_id"] for item in storage_info["items"]
    }


def st_process_uploaded_files(uploaded_files: list[UploadedFile]) -> None:
    for file in uploaded_files:
        response = add_document(file)
        status = get_uploading_status(response["documentID"])["status"]

        with st.spinner(f"Файл {file.name} загружается... Пожалуйста, подождите"):
            while status == "Processing":
                time.sleep(1)
                status = get_uploading_status(response["documentID"])["status"]

        if status == "Added":
            st.success(f"Успешно добавлен документ {file.name}")
        elif status == "NotFound":
            st.warning(f"Произошла ошибка при добавлении документа {file.name}")
        else:
            st.error(f"Что-то пошло не так. Статус: {status}")


def st_process_query(query: str, document_ids: list[str]) -> None:
    st.header("Ответ LLM:")
    # TODO: add LLM answer handling
    st.markdown("ТекстТекстТекст")

    response = search_query(query, document_ids)
    doc_id2filename = get_doc_id2filename()

    st.header("Результаты поиска:")

    for res in response["results"]:
        st.subheader(
            f"Документ {doc_id2filename[res['document_id']]}, страница {res['page']}:"
        )
        st.markdown(res["text"])


def main() -> None:
    st.title("Приложение для ответов на вопросы по документам")

    with st.form("upload_files_key"):
        uploaded_files = st.file_uploader(
            "Загрузите документы:", type=["pdf", "docx"], accept_multiple_files=True
        )
        button = st.form_submit_button("Подтвердить")

    if button and uploaded_files is not None:
        st_process_uploaded_files(uploaded_files)

    doc_filename2id = get_doc_filename2id()
    selected_documents = st.multiselect("Выберите документы:", doc_filename2id.keys())

    with st.form("search_query_key"):
        query = st.text_area("Введите запрос:", height=100)
        button = st.form_submit_button("Найти")

    if button:
        document_ids = [doc_filename2id[name] for name in selected_documents]
        st_process_query(query, document_ids)


if __name__ == "__main__":
    st.set_page_config(layout="centered")
    logging.basicConfig(level=logging.INFO)
    main()
