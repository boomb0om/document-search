from document_search.entities import DocEntity, TextDocEntity


class EntityProcessor:
    @staticmethod
    def filter_short_entities(
        entities: list[DocEntity], max_len: int = 3
    ) -> list[DocEntity]:
        return list(
            filter(
                lambda x: not isinstance(x, TextDocEntity) or len(x.text) > max_len,
                entities,
            )
        )

    @staticmethod
    def merge_text_entities(entities: list[DocEntity]) -> list[DocEntity]:
        curr_entity = None
        new_entities = []

        for entity in entities:
            if isinstance(entity, TextDocEntity):
                if curr_entity is not None:
                    if entity.text[0].islower() and curr_entity.text[-1] not in (
                        ".",
                        ";",
                    ):
                        curr_entity.text += f" {entity.text}"
                    else:
                        curr_entity.text = curr_entity.text.replace("\xad", "-")
                        new_entities.append(curr_entity)
                        curr_entity = entity
                else:
                    curr_entity = entity
            else:
                new_entities.append(entity)

        return new_entities
