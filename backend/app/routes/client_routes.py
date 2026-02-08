"""
Client Routes
API endpoints for managing clients and payments
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.services.client_service import ClientService
from app.models.client_models import (
    ClientCreate, ClientUpdate, ClientResponse, ClientListResponse,
    PaymentCreate, PaymentResponse
)

from app.core.dependencies import get_current_active_user

router = APIRouter()

# =====================
# CLIENT ENDPOINTS
# =====================

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new client.
    Requires Admin or Employee privileges (handled by RoleRights in frontend, 
    but ideally we should check permissions here too).
    """
    # TODO: Add permission check (e.g., using RoleRights service)
    return ClientService.create_client(
        client_data, 
        created_by=str(current_user["user_id"]),
        tenant_id=str(current_user["tenant_id"])
    )

@router.get("/", response_model=ClientListResponse)
async def get_clients(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: str = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get all clients with pagination and search
    """
    items, total = ClientService.get_all_clients(page, size, search)
    return ClientListResponse(
        items=items,
        total=total,
        page=page,
        size=size
    )

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get client details by ID
    """
    client = ClientService.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update client details
    """
    client = ClientService.update_client(client_id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Soft delete a client
    """
    success = ClientService.delete_client(client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return
    
@router.post("/{client_id}/reset-password", status_code=status.HTTP_200_OK)
async def reset_client_password(
    client_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Reset client password (Admin only ideally)
    """
    success = ClientService.reset_client_password(client_id, updated_by=str(current_user["user_id"]))
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Password reset successfully and emailed to client"}

# =====================
# PAYMENT ENDPOINTS
# =====================

@router.post("/{client_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def record_payment(
    client_id: int,
    payment_data: PaymentCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Record a payment for a client
    """
    if payment_data.client_id != client_id:
        raise HTTPException(status_code=400, detail="Client ID mismatch")
        
    return ClientService.record_payment(payment_data, created_by=str(current_user["user_id"]))

@router.get("/{client_id}/payments", response_model=List[PaymentResponse])
async def get_client_payments(
    client_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get payment history for a client
    """
    return ClientService.get_client_payments(client_id)
