from ninja import Schema


class ConsentData(Schema):
    id: str
    dynamic_client_id: str
    status: str
    token: str
