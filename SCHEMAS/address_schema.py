from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

class EnderecoCompleto(BaseModel):

    rua: str
    bairro: str
    estado: str
    numero: str
    complemento: Optional[str] = None
    cep: str

    model_config = ConfigDict(
            from_attributes=True,      
            extra="forbid",            
            validate_assignment=True,  
            str_strip_whitespace=True, 
            frozen=True,
        )


class EnderecoResponse(BaseModel):
    id_endereco: int
    rua: str
    bairro: str
    estado: str
    numero: str
    complemento: Optional[str] = None
    cep: str


class EnderecoCepResponse(BaseModel):
    rua: str
    bairro: str
    estado: str
    numero: Optional[str] = None
    complemento: Optional[str] = None
    cep: str