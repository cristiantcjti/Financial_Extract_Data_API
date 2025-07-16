from dataclasses import dataclass, field

from requests import PreparedRequest, Response


@dataclass
class IntegrationResultDTO:
    success: bool = field(default=False)
    request: PreparedRequest | None = None
    response: Response | None = None
    additional_data: dict = field(default_factory=dict)
