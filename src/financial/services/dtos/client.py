from ninja import Schema


class DynamicClientData(Schema):
    id: str
    name: str
    token: str
    organization_name: str
    organization_type: str
