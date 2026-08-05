from pydantic import BaseModel, ConfigDict
from datetime import date
from SCHEMAS.address_schema import EnderecoResponse

class UserResponse(BaseModel):
    id_usuario: int
    nome_completo: str
    login: str
    data_nascimento: date
    enderecos: list[EnderecoResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )