from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config.database_config import get_db
from models.tables_models import FormResponse
from utiles.schemas import FormCreate, FormUpdate, FormResponseSchema
from routes.auth_routes import get_current_user
from models.tables_models import User

router = APIRouter(prefix="/forms", tags=["forms"])


@router.post("/", response_model=FormResponseSchema, status_code=status.HTTP_201_CREATED)
def create_form_response(payload: FormCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_form = FormResponse(**payload.model_dump(), user_id=current_user.id)
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form


@router.get("/", response_model=List[FormResponseSchema])
def list_form_responses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(FormResponse)
        .filter(FormResponse.user_id == current_user.id)
        .order_by(FormResponse.id.desc())
        .all()
    )


@router.get("/{form_id}", response_model=FormResponseSchema)
def get_form_response(form_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = (
        db.query(FormResponse)
        .filter(FormResponse.id == form_id, FormResponse.user_id == current_user.id)
        .first()
    )
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form response not found")
    return form


@router.put("/{form_id}", response_model=FormResponseSchema)
def update_form_response(form_id: int, payload: FormUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = (
        db.query(FormResponse)
        .filter(FormResponse.id == form_id, FormResponse.user_id == current_user.id)
        .first()
    )
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form response not found")
    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    for key, value in update_data.items():
        setattr(form, key, value)
    db.add(form)
    db.commit()
    db.refresh(form)
    return form


@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_form_response(form_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = (
        db.query(FormResponse)
        .filter(FormResponse.id == form_id, FormResponse.user_id == current_user.id)
        .first()
    )
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form response not found")
    db.delete(form)
    db.commit()
    return None


