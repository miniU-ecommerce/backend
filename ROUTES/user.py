from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from httpx import AsyncClient
from re import sub

from DEPENDENCIES import verificar_token, pegar_sessao
from MODELS import Usuarios, Enderecos
from SCHEMAS.user_schema import UserResponse
from SCHEMAS.address_schema import EnderecoCompleto, EnderecoResponse, EnderecoCepResponse

user_router = APIRouter(prefix="/user", tags=["Usuarios"])


@user_router.get("/", response_model=UserResponse)
async def buscar_informacoes_usuario(db: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    info_usuario = (
        db.query(Usuarios)
        .options(joinedload(Usuarios.enderecos))
        .filter(Usuarios.id_usuario == usuario.id_usuario)
        .first()
    )
    
    if not info_usuario:
        raise HTTPException(status_code=404, detail="Usuário não logado ou não encontrado.")
    return info_usuario


@user_router.post("/endereco", response_model=EnderecoResponse)
async def adicionar_endereco_usuario(endereco_schema: EnderecoCompleto, db: Session = Depends(pegar_sessao), usuario: Usuarios = Depends(verificar_token)):
    # Garatindo que o cep tenha o formato correto, apenas números.
    cep_normalizado = sub(r"\D", "", endereco_schema.cep)
    
    endereco = (
        db.query(Enderecos)
        .filter(Enderecos.id_usuario==usuario.id_usuario)
        .filter(
            Enderecos.cep==cep_normalizado,
            Enderecos.numero==endereco_schema.numero
        )
        .first()
    )
    
    if endereco:
        raise HTTPException(status_code=400, detail="Endereço já existe para esse usuário.")
    
    novo_endereco = Enderecos(
        id_usuario=usuario.id_usuario,
        rua=endereco_schema.rua,
        bairro=endereco_schema.bairro,
        estado=endereco_schema.estado,
        numero=endereco_schema.numero,
        complemento=endereco_schema.complemento,
        cep=cep_normalizado
    )
    
    db.add(novo_endereco)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Não foi possível cadastrar o endereço.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado.")
    
    db.refresh(novo_endereco)
    return novo_endereco


@user_router.delete("/endereco/{id_endereco}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_endereco_usuario(
    id_endereco: int,
    db: Session = Depends(pegar_sessao),
    usuario: Usuarios = Depends(verificar_token)
):
    endereco = (
        db.query(Enderecos)
        .filter(
            Enderecos.id_endereco == id_endereco,
            Enderecos.id_usuario == usuario.id_usuario
        )
        .first()
    )

    if not endereco:
        raise HTTPException(status_code=404, detail="Endereço não encontrado.")

    db.delete(endereco)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado ao deletar o endereço.")

    return None


@user_router.get("/cep/{cep}", response_model=EnderecoCepResponse)
async def buscar_endereco_cep(cep: str):
    # Fazendo requisição
    async with AsyncClient() as client:
        response = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
        dados_endereco = response.json()
    
    if dados_endereco.get("erro"):
        raise HTTPException(status_code=404, detail="Endereço não encontrado")
    
    endereco = EnderecoCepResponse(
        rua=dados_endereco.get("logradouro"),
        bairro=dados_endereco.get("bairro"),
        estado=dados_endereco.get("uf"),
        complemento=dados_endereco.get("complemento"),
        cep=dados_endereco.get("cep")
    )
    
    return endereco