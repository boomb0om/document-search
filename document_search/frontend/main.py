import logging
import time

import streamlit as st
from api import (
    add_document,
    get_image_by_id,
    get_storage_info,
    get_uploading_status,
    search_query,
)
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile


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
    response = search_query(
        query, None if len(document_ids) == 0 else document_ids, use_rag=True
    )
    st.header("Ответ LLM:")
    st.markdown(response["llm_answer"])

    doc_id2filename = get_doc_id2filename()
    st.header("Результаты поиска:")

    for res in response["results"]:
        st.subheader(
            f"Документ {doc_id2filename[res['document_id']]}, страница {res['page']}:"
        )
        st.markdown(res["text"])
        with st.expander("Посмотреть страницу"):
            image_bytes = get_image_by_id(res["document_id"], res["page"])
            image = Image.open(image_bytes).convert("RGB")
            st.image(image)


def main() -> None:
    st.title("Приложение для ответов на вопросы по документам")

    storage_info = get_storage_info()
    with st.sidebar:
        with st.expander("Посмотреть документы в базе"):
            for item in storage_info["items"]:
                st.subheader(item["document_filename"])

    with st.form("upload_files_key"):
        uploaded_files = st.file_uploader(
            "Загрузите документы:", type=["pdf", "docx"], accept_multiple_files=True
        )
        button = st.form_submit_button("Подтвердить")

    if button and uploaded_files is not None:
        st_process_uploaded_files(uploaded_files)

    doc_filename2id = get_doc_filename2id()
    selected_documents = st.multiselect(
        "Выберите документы, по которым будет осуществлён поиск:",
        doc_filename2id.keys(),
    )

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
