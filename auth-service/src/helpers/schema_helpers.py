def add_metadata_to_fields(**metadata):
    def decorator(cls):
        for field in cls.model_fields.values():
            if not field.json_schema_extra:
                field.json_schema_extra = {}
            field.json_schema_extra.update(metadata)
        return cls

    return decorator
