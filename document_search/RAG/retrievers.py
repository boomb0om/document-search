from langchain.chains import ConversationalRetrievalChain
from langchain_community.llms import YandexGPT
from langchain.text_splitter import RecursiveCharacterTextSplitter
from document_search.search import TextEntityEmbedderE5
from document_search.storages import DocumentStorageE5

import getpass


class RAGRetriever:
    def __init__(self, embedder: TextEntityEmbedderE5, storage: DocumentStorageE5):
        self.embedder = embedder
        self.storage = storage
        iam_token = getpass.getpass()
        self.llm = YandexGPT(iam_token=iam_token, folder_id='b1g5kpnfuptevfeqk1nm')
        self.vector_store = storage.vector_store

    def get_context_for_query(self, query: str, k: int, context_length: int) -> str:
        retrieved_entities = self.storage.get_relevant_entities(query, k)
        context_list = []
        for entity in retrieved_entities:
            entity_context = self.storage.retrieve_context(entity.position, context_length)
            context_list.append(entity_context)
        full_context = "\n".join(context_list)
        return full_context

    def retrieve_answer(self, query: str, k: int = 1, context_length: int = 1) -> str:
        context = self.get_context_for_query(query, k, context_length)
        # retriever = ConversationalRetrievalChain(
        #     retriever=self.vector_store,
        #     text_splitter=RecursiveCharacterTextSplitter(),
        #     llm=self.llm,
        #     retriever_mode="answer_question"
        # )
        answer = self.llm(context + "\n" + query)
        return answer
