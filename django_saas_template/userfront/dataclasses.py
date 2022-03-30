import dataclasses


@dataclasses.dataclass(frozen=True)
class UserfrontUser:
    uuid: str
    tenant_id: str
    username: str
    name: str
    email: str
    image: str


@dataclasses.dataclass(frozen=True)
class UserfrontTenant:
    tenant_id: str
    name: str
    image: str
