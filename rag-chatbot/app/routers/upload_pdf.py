from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from app.controllers.upload_pdf import PDFController
from app.dependencies import get_pdf_controller

router = APIRouter()

@router.post("/upload_pdf/")
async def upload_pdf(
    emp_id: str = Form(...),
    file: UploadFile = File(...),
    controller: PDFController = Depends(get_pdf_controller)
):
    try:
        return await controller.process_pdf(file, emp_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/retrieve_documents/")
async def get_pdf_documents(controller: PDFController = Depends(get_pdf_controller)):
    try:
        return controller.get_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


@router.get("/retrieve_single_document")
async def get_pdf_documents_by_emp_id(emp_id: str, controller: PDFController = Depends(get_pdf_controller)):
    try:
        return controller.get_documents_by_emp_id(emp_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
