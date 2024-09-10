from document_search.entities import DocEntity, TextDocEntity


class EntityProcessor:
    @staticmethod
    def filter_short_entities(
        entities: list[DocEntity], min_len: int = 8
    ) -> list[DocEntity]:
        return list(
            filter(
                lambda x: not isinstance(x, TextDocEntity) or len(x.text) >= min_len,
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
                    if entity.text[0].islower() and curr_entity.text[-1] not in (".", ";", ":"):
                        if curr_entity.text[-1] in ("\xad", "-"):
                            curr_entity.text = curr_entity.text[:-1]
                        else:
                            curr_entity.text += " "
                        curr_entity.text += entity.text
                    else:
                        curr_entity.text = curr_entity.text.replace("\xad", "-")
                        new_entities.append(curr_entity)
                        curr_entity = entity
                else:
                    curr_entity = entity
            else:
                new_entities.append(entity)

        if isinstance(curr_entity, TextDocEntity):
            new_entities.append(curr_entity)

        return new_entities
