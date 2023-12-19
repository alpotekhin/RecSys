import pickle
import random
import pandas as pd

from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from service.api.credentials import get_token
from service.api.exceptions import AuthenticationError, ModelNotFoundError, UserNotFoundError
from service.api.responses import HealthResponse, NotFoundResponse, RecoResponse, UnauthorizedResponse
from service.api.utils import get_knn_online_reco, get_model_names, get_popular_rec, get_model_offline_reco
from service.log import app_logger

router = APIRouter()
security = HTTPBearer()
secret_token = get_token()


with open("service/recmodels/tfidf_knn.pkl", "rb") as file:
    knn_model = pickle.load(file)
    
with open("service/recmodels/most_popular.pkl", "rb") as file:
    pop_recs = pickle.load(file)

with open("service/recmodels/knn_preds.pkl", "rb") as file:
    knn_preds = pickle.load(file)

with open("service/recmodels/vector_recs.pkl", "rb") as file:
    vector_preds = pickle.load(file)
    
with open("service/recmodels/dssm_recs.pkl", "rb") as file:
    dssm_preds = pickle.load(file)

with open("service/recmodels/encoder_recs.pkl", "rb") as file:
    encoder_preds = pickle.load(file)
    
with open("service/recmodels/ranker_recs.pkl", "rb") as file:
    ranker_preds = pickle.load(file)
    
async def read_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials.credentials == secret_token:
        return credentials.credentials
    raise AuthenticationError()


@router.get(
    path="/health",
    tags=["Health"],
    responses={
        status.HTTP_200_OK: {"model": HealthResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
    },
)
async def health(token: str = Depends(read_current_user)) -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses={
        status.HTTP_200_OK: {"model": RecoResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
        status.HTTP_404_NOT_FOUND: {"model": NotFoundResponse},
    },
)
async def get_reco(
    request: Request, model_name: str, user_id: int, token: str = Depends(read_current_user)
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
    elif model_name == "knn":
        reco = get_knn_online_reco(user_id, knn_preds)
        if not reco:
            reco = get_popular_rec(user_id, pop_recs)
        if len(reco) < 10:
            reco = list(pd.unique(reco + get_popular_rec(user_id, pop_recs)))[:10]
    elif model_name == "vector":
        reco = vector_preds[user_id]
        if not reco:
            reco = get_popular_rec(user_id, pop_recs)
        if len(reco) < 10:
            reco = list(pd.unique(reco + get_popular_rec(user_id, pop_recs)))[:10]
    elif model_name == "dssm":
        reco = dssm_preds[user_id]
        if not reco:
            reco = get_popular_rec(user_id, pop_recs)
        if len(reco) < 10:
            reco = list(pd.unique(reco + get_popular_rec(user_id, pop_recs)))[:10]
    elif model_name == "encoder":
        reco = encoder_preds[user_id]
        if not reco:
            reco = get_popular_rec(user_id, pop_recs)
        if len(reco) < 10:
            reco = list(pd.unique(reco + get_popular_rec(user_id, pop_recs)))[:10]
    elif model_name == "ranker":
        reco = ranker_preds[user_id]
        if not reco:
            reco = get_popular_rec(user_id, pop_recs)
        if len(reco) < 10:
            reco = list(pd.unique(reco + get_popular_rec(user_id, pop_recs)))[:10]

    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
