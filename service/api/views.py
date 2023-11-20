import random
from typing import List

from fastapi import APIRouter, FastAPI, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from service.api.exceptions import ModelNotFoundError, UserNotFoundError
from service.log import app_logger
from service.api.utils import get_model_names
from service.api.credentials import get_token

class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()
bearer_scheme = HTTPBearer()
secret_token = get_token()


async def read_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    if credentials.credentials == secret_token:
        return credentials.credentials
    raise ValueError()

@router.get(
    path="/health",
    tags=["Health"],

)
async def health(token: str = Depends(read_current_user)) -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    status_code=status.HTTP_200_OK,
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: str = Depends(read_current_user)
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    # Write your code here
    existing_models = get_model_names()
    
    if model_name not in existing_models:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")
        
    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")
    
    if model_name == "dummy":
        reco = random.sample(range(100), 10)
    
    # k_recs = request.app.state.k_recs
    # reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
