from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from services import get_db, get_user_by_email, create_token, get_current_user, service_create_lead, service_get_leads, \
                    service_delete_lead, service_update_lead, authenticate_user, create_user_in_db, get_lead
from schemas import UserCreate, User, Lead, LeadCreate

app = FastAPI()


@app.post("/api/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = await get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    created_user = await create_user_in_db(user, db) 

    return await create_token(created_user)


@app.post("/api/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    return await create_token(user)


@app.get("/api/users/me", response_model=User)
async def get_user(user: User = Depends(get_current_user)):
    return user

@app.post("/api/leads", response_model=Lead)
async def create_lead(lead: LeadCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await service_create_lead(user=user, db=db, lead=lead)

@app.get("/api/leads", response_model=List[Lead])
async def get_leads(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await service_get_leads(user=user, db=db)

@app.get("/api/leads/{lead_id}", status_code=200)
async def get_lead_individual(lead_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await get_lead(lead_id, user, db)


@app.delete("/api/leads/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await service_delete_lead(lead_id, user, db)
    return {"message", "Successfully Deleted"}


@app.put("/api/leads/{lead_id}", status_code=200)
async def update_lead(lead_id: int, lead: LeadCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await service_update_lead(lead_id, lead, user, db)
    return {"message", "Successfully Updated"}


@app.get("/api")
async def root():
    return {"message": "Awesome Leads Manager"}
