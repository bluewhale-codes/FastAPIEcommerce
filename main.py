from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import cloudinary
import cloudinary.uploader
import json

# -------------------------------------
# Cloudinary Configuration
# -------------------------------------
cloudinary.config(
    cloud_name="dycjjaxsk",      # Replace with your Cloudinary cloud name
    api_key="325247431186386",            # Replace with your API key
    api_secret="WEMuN15iF5KQYEeUXyJX0ES-KUA"       # Replace with your API secret
)

# -------------------------------------
# Database Configuration
# -------------------------------------
DATABASE_URL = "mysql+mysqlconnector://root:chandigarhPB%40123@localhost:3306/ecommerce_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -------------------------------------
# FastAPI App
# -------------------------------------
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------
# SQLAlchemy Model
# -------------------------------------
class ProductTable(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    description = Column(String(500))
    price = Column(Float)
    discount_percent = Column(Float, default=0.0)
    final_price = Column(Float)
    category = Column(String(100))
    brand = Column(String(100))
    stock = Column(Integer)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    tags = Column(JSON)
    color = Column(String(50))
    size = Column(String(50))
    weight = Column(Float)
    dimensions = Column(JSON)
    image_url = Column(String(255))
    images = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

# -------------------------------------
# Pydantic Schemas
# -------------------------------------
class Dimensions(BaseModel):
    length: float
    width: float
    height: float

# -------------------------------------
# Helper Function: Upload to Cloudinary
# -------------------------------------
def upload_to_cloudinary(file: UploadFile) -> dict:
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="products",  # Cloudinary folder name
            resource_type="auto"
        )
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

# -------------------------------------
# Dependency: Database Session
# -------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------
# POST: Upload Single Image
# -------------------------------------
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload single image to Cloudinary"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    result = upload_to_cloudinary(file)
    return {"message": "Image uploaded successfully", "url": result["url"]}

# -------------------------------------
# POST: Upload Multiple Images
# -------------------------------------
@app.post("/upload-images")
async def upload_multiple_images(files: List[UploadFile] = File(...)):
    """Upload multiple images to Cloudinary"""
    uploaded_urls = []
    
    for file in files:
        if not file.content_type.startswith("image/"):
            continue
        result = upload_to_cloudinary(file)
        uploaded_urls.append(result["url"])
    
    return {
        "message": f"{len(uploaded_urls)} images uploaded successfully",
        "urls": uploaded_urls
    }

# -------------------------------------
# POST: Add Product with Images
# -------------------------------------
@app.post("/add-product")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    discount_percent: float = Form(0.0),
    category: str = Form(...),
    brand: str = Form(...),
    stock: int = Form(...),
    rating: float = Form(0.0),
    reviews_count: int = Form(0),
    tags: str = Form("[]"),  # JSON string
    color: Optional[str] = Form(None),
    size: Optional[str] = Form(None),
    weight: Optional[float] = Form(None),
    dimensions: Optional[str] = Form(None),  # JSON string
    is_active: bool = Form(True),
    main_image: UploadFile = File(...),
    additional_images: List[UploadFile] = File(None)
):
    db = next(get_db())
    
    # Upload main image
    main_image_result = upload_to_cloudinary(main_image)
    image_url = main_image_result["url"]
    
    # Upload additional images
    additional_urls = []
    if additional_images:
        for img in additional_images:
            if img.filename:  # Check if file exists
                result = upload_to_cloudinary(img)
                additional_urls.append(result["url"])
    
    # Parse JSON strings
    tags_list = json.loads(tags) if tags else []
    dimensions_dict = json.loads(dimensions) if dimensions else None
    
    # Calculate final price
    final_price = price - (price * discount_percent / 100) if discount_percent else price
    
    # Create product
    new_product = ProductTable(
        name=name,
        description=description,
        price=price,
        discount_percent=discount_percent,
        final_price=final_price,
        category=category,
        brand=brand,
        stock=stock,
        rating=rating,
        reviews_count=reviews_count,
        tags=tags_list,
        color=color,
        size=size,
        weight=weight,
        dimensions=dimensions_dict,
        image_url=image_url,
        images=additional_urls,
        is_active=is_active
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return {
        "message": "✅ Product added successfully!",
        "product_id": new_product.id,
        "image_url": image_url,
        "additional_images": additional_urls
    }

# -------------------------------------
# GET: All Products
# -------------------------------------
@app.get("/products")
def get_products():
    db = next(get_db())
    products = db.query(ProductTable).all()
    return {"products": products}
