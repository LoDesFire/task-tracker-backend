from pydantic import BaseModel


class DetailRecordSchema(BaseModel):
    msg: str
    type: str


class DetailSchema(BaseModel):
    """
    Schema for the message or error responses
    """

    @classmethod
    def error(cls, error_message: str):
        detail_records = [DetailRecordSchema(msg=error_message, type="error")]
        return cls(detail=detail_records)

    detail: list[DetailRecordSchema]
