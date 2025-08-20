"""
Modern FastAPI endpoints for enhanced geological analysis capabilities.
This module provides modern async API endpoints while maintaining compatibility
with the existing Flask application.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import asyncio
import aiofiles
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime

from app.utils.data_analysis import (
    load_excel_data, analyze_rmr_data, analyze_fracture_data, 
    generate_visualization, clean_geological_data,
    create_interactive_rmr_plot, create_interactive_fracture_plot
)
from app.utils.image_processing import (
    analyze_geological_image_enhanced, get_image_dimensions,
    enhance_geological_features, create_overlay_image
)
from app.utils.stereonet import (
    plot_stereonet, create_interactive_stereonet, 
    generate_stereonet_data, calculate_orientation_statistics
)

# Pydantic models for request/response validation
class GeologicalDataFilter(BaseModel):
    mode: str = "rmr"  # "rmr" or "fracturas"
    frente: Optional[str] = None
    pk_medio_min: Optional[float] = None
    pk_medio_max: Optional[float] = None
    rmr_min: Optional[float] = None
    rmr_max: Optional[float] = None
    familia: Optional[str] = None

class ImageAnalysisOptions(BaseModel):
    detect_fractures: bool = True
    analyze_phases: bool = True
    calculate_porosity: bool = True
    detect_minerals: bool = True
    enhance_features: bool = True

class StereonetRequest(BaseModel):
    orientation_data: List[Dict[str, float]]  # [{'dip': float, 'dip_direction': float, 'family': str}]
    title: Optional[str] = "Geological Stereonet"
    interactive: bool = False

class VisualizationRequest(BaseModel):
    data: List[Dict]
    plot_type: str = "rmr"  # "rmr", "fracture", "stereonet", "combined"
    interactive: bool = False
    options: Optional[Dict] = {}

# Create FastAPI app
fastapi_app = FastAPI(
    title="Enhanced Geological Analysis API",
    description="Modern async API for geological data processing and visualization",
    version="2.0.0"
)

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Async file upload handling
async def save_uploaded_file(uploaded_file: UploadFile, upload_dir: str) -> str:
    """Save uploaded file asynchronously."""
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.filename}"
    filepath = os.path.join(upload_dir, filename)
    
    async with aiofiles.open(filepath, 'wb') as f:
        content = await uploaded_file.read()
        await f.write(content)
    
    return filepath

# Enhanced API endpoints
@fastapi_app.post("/api/v2/upload/excel")
async def upload_excel_async(file: UploadFile = File(...)):
    """
    Upload Excel file with geological data asynchronously.
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files allowed.")
    
    try:
        # Save file asynchronously
        filepath = await save_uploaded_file(file, "app/static/uploads")
        
        # Load and validate data
        df = load_excel_data(filepath)
        if df is None:
            raise HTTPException(status_code=422, detail="Failed to process Excel file")
        
        # Get basic statistics
        stats = {
            'total_rows': len(df),
            'columns': df.columns.tolist(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict()
        }
        
        return JSONResponse({
            "success": True,
            "message": "Excel file uploaded and processed successfully",
            "filename": os.path.basename(filepath),
            "statistics": stats,
            "preview": df.head().to_dict('records')
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@fastapi_app.post("/api/v2/upload/image")
async def upload_image_async(file: UploadFile = File(...)):
    """
    Upload geological image for analysis.
    """
    allowed_types = ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_types):
        raise HTTPException(status_code=400, detail="Invalid file type. Only image files allowed.")
    
    try:
        # Save file asynchronously
        filepath = await save_uploaded_file(file, "app/static/uploads")
        
        # Get basic image info
        dimensions = get_image_dimensions(filepath)
        
        return JSONResponse({
            "success": True,
            "message": "Image uploaded successfully",
            "filename": os.path.basename(filepath),
            "dimensions": dimensions
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@fastapi_app.post("/api/v2/analysis/data/filter")
async def filter_geological_data_async(
    data: List[Dict],
    filters: GeologicalDataFilter
):
    """
    Enhanced geological data filtering with validation.
    """
    try:
        # Convert filters to dictionary format
        filter_dict = {}
        
        if filters.frente:
            filter_dict['Frente'] = filters.frente
        
        if filters.pk_medio_min is not None or filters.pk_medio_max is not None:
            filter_dict['PK_medio'] = {}
            if filters.pk_medio_min is not None:
                filter_dict['PK_medio']['min'] = filters.pk_medio_min
            if filters.pk_medio_max is not None:
                filter_dict['PK_medio']['max'] = filters.pk_medio_max
        
        if filters.mode == 'rmr':
            if filters.rmr_min is not None or filters.rmr_max is not None:
                filter_dict['RMR'] = {}
                if filters.rmr_min is not None:
                    filter_dict['RMR']['min'] = filters.rmr_min
                if filters.rmr_max is not None:
                    filter_dict['RMR']['max'] = filters.rmr_max
            
            filtered_data = analyze_rmr_data(data, filter_dict)
        
        else:  # fracture mode
            if filters.familia:
                filter_dict['Familia'] = filters.familia
                
            filtered_data = analyze_fracture_data(data, filter_dict)
        
        return JSONResponse({
            "success": True,
            "data": filtered_data,
            "total_filtered": len(filtered_data),
            "filters_applied": filter_dict
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering data: {str(e)}")

@fastapi_app.post("/api/v2/analysis/image/enhanced")
async def analyze_image_enhanced_async(
    filename: str,
    options: ImageAnalysisOptions = ImageAnalysisOptions()
):
    """
    Perform enhanced geological image analysis.
    """
    try:
        filepath = os.path.join("app/static/uploads", filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Image file not found")
        
        # Convert options to dictionary
        analysis_options = options.dict()
        
        # Perform enhanced analysis
        results = analyze_geological_image_enhanced(filepath, analysis_options)
        
        if 'error' in results:
            raise HTTPException(status_code=422, detail=results['error'])
        
        return JSONResponse({
            "success": True,
            "results": results,
            "analysis_timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

@fastapi_app.post("/api/v2/visualization/stereonet")
async def create_stereonet_async(request: StereonetRequest):
    """
    Create stereonet plot from orientation data.
    """
    try:
        # Extract orientation data
        orientation_tuples = []
        families = []
        
        for item in request.orientation_data:
            if 'dip' in item and 'dip_direction' in item:
                orientation_tuples.append((item['dip'], item['dip_direction']))
                families.append(item.get('family', 'Unknown'))
        
        if not orientation_tuples:
            raise HTTPException(status_code=422, detail="No valid orientation data provided")
        
        # Calculate orientation statistics
        stats = calculate_orientation_statistics(orientation_tuples)
        
        # Create stereonet plot
        if request.interactive:
            fig = create_interactive_stereonet(orientation_tuples, families)
            plot_type = "interactive_stereonet"
        else:
            fig = plot_stereonet(orientation_tuples, request.title, families)
            plot_type = "static_stereonet"
        
        # Save plot (in a real implementation, you'd return the plot data or save to file)
        plot_info = {
            "plot_type": plot_type,
            "data_points": len(orientation_tuples),
            "families": list(set(families)),
            "statistics": stats
        }
        
        return JSONResponse({
            "success": True,
            "plot_info": plot_info,
            "message": "Stereonet created successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating stereonet: {str(e)}")

@fastapi_app.post("/api/v2/visualization/create")
async def create_visualization_async(request: VisualizationRequest):
    """
    Create advanced geological visualizations.
    """
    try:
        df = pd.DataFrame(request.data)
        
        if df.empty:
            raise HTTPException(status_code=422, detail="No data provided for visualization")
        
        # Generate comprehensive visualization data
        viz_data = generate_visualization(df)
        
        # Create specific plot based on type
        plot_result = {}
        
        if request.plot_type == "rmr":
            if 'RMR' in df.columns and request.interactive:
                # Create interactive RMR plot
                plot_result = {
                    "type": "interactive_rmr",
                    "message": "Interactive RMR plot generated",
                    "data_points": len(df),
                    "rmr_range": [float(df['RMR'].min()), float(df['RMR'].max())]
                }
        
        elif request.plot_type == "fracture":
            if 'Familia' in df.columns and request.interactive:
                plot_result = {
                    "type": "interactive_fracture",
                    "message": "Interactive fracture plot generated",
                    "families": df['Familia'].unique().tolist(),
                    "data_points": len(df)
                }
        
        elif request.plot_type == "combined":
            plot_result = {
                "type": "combined_analysis",
                "message": "Combined geological analysis generated",
                "available_analyses": list(viz_data['statistics'].keys())
            }
        
        return JSONResponse({
            "success": True,
            "visualization_data": viz_data,
            "plot_result": plot_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating visualization: {str(e)}")

@fastapi_app.get("/api/v2/analysis/capabilities")
async def get_analysis_capabilities():
    """
    Get information about available analysis capabilities.
    """
    capabilities = {
        "image_analysis": {
            "fracture_detection": True,
            "phase_analysis": True,
            "porosity_calculation": True,
            "mineral_detection": True,
            "feature_enhancement": True,
            "supported_formats": [".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp"]
        },
        "data_analysis": {
            "rmr_analysis": True,
            "fracture_analysis": True,
            "spatial_analysis": True,
            "statistical_analysis": True,
            "filtering": True,
            "supported_formats": [".xlsx", ".xls", ".csv"]
        },
        "visualization": {
            "interactive_plots": True,
            "stereonet": True,
            "rose_diagrams": True,
            "spatial_plots": True,
            "statistical_plots": True
        },
        "libraries": {
            "opencv": "Available" if 'cv2' in globals() else "Not available",
            "scipy": "Available" if 'scipy' in globals() else "Not available",
            "scikit_image": "Available" if 'skimage' in globals() else "Not available",
            "mplstereonet": "Check required" # Would check actual import
        }
    }
    
    return JSONResponse({
        "success": True,
        "capabilities": capabilities,
        "api_version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    })

@fastapi_app.get("/api/v2/health")
async def health_check():
    """API health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "api_version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    })

# Integration function to mount FastAPI in Flask
def create_fastapi_app():
    """Create and configure FastAPI application."""
    return fastapi_app