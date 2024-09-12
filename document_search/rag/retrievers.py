from typing import Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import YandexGPT

from document_search.entities import DocEntity
from document_search.search import TextEntityEmbedderE5
from document_search.storages import DocumentStorageE5

from .credentials import YANDEX_FOLDER_ID, YANDEX_GPT_KEY  # type: ignore
from .prompt import RAG_SYSTEM_PROMPT


class YandexGPTRetriever:
    def __init__(self, embedder: TextEntityEmbedderE5, storage: DocumentStorageE5):
        self.embedder = embedder
        self.storage = storage
        self.llm = YandexGPT(api_key=YANDEX_GPT_KEY, folder_id=YANDEX_FOLDER_ID, model_name='yandexgpt')  # type: ignore

        prompt_template_str = RAG_SYSTEM_PROMPT

        self.prompt = PromptTemplate(
            input_variables=["query", "context"],
            template=prompt_template_str,
        )
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.vector_store = storage.vector_store

    def get_context_for_entities(self, entities: list[DocEntity], context_length: int) -> str:
        context_list = []
        for entity in entities:
            entity_context = self.storage.retrieve_context(entity.position, context_length)
            context_list.append(entity_context)
        full_context = "\n".join(context_list)
        return full_context

    def retrieve_answer(
        self, 
        query: str, 
        k: int = 5, 
        rag_k: int = 1, 
        context_length: int = 1,
        document_ids: Optional[list[str]] = None
    ) -> str:
        retrieved_data = self.storage.get_relevant_entities(query, k, document_ids)
        context = self.get_context_for_entities([entity for entity, _ in retrieved_data][:rag_k], context_length)

        answer: str = self.llm_chain.run(
            {
                'query': query,
                'context': context
            }
        )
        return answer

    def retrieve_answer_detailed(
        self,
        query: str,
        k: int = 5,
        rag_k: int = 1,
        context_length: int = 1,
        document_ids: Optional[list[str]] = None
    ) -> tuple[list[tuple[DocEntity, float]], str]:
        retrieved_data = self.storage.get_relevant_entities(query, k, document_ids)
        context = self.get_context_for_entities([entity for entity, _ in retrieved_data][:rag_k], context_length)

        answer = self.llm_chain.run(
            {
                'query': query,
                'context': context
            }
        )
        return retrieved_data, answer
