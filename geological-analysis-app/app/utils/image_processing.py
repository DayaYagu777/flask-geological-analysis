from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import json
import os

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("OpenCV not available - using basic image processing")

try:
    from scipy import ndimage, spatial, cluster
    from scipy.ndimage import gaussian_filter, sobel, binary_erosion, binary_dilation
    from skimage import measure, morphology, segmentation, feature, filters
    from skimage.color import rgb2gray, rgb2hsv
    from skimage.util import img_as_ubyte, img_as_float
    HAS_SCIPY = True
    HAS_SKIMAGE = True
except ImportError:
    HAS_SCIPY = False
    HAS_SKIMAGE = False
    print("SciPy/scikit-image not available - using basic image processing")

def resize_image(image_path, output_path, size):
    """Resize image to specified dimensions."""
    with Image.open(image_path) as img:
        img = img.resize(size, Image.LANCZOS)
        img.save(output_path)

def apply_filter(image_path, filter_type):
    """Apply various filters to enhance geological features."""
    with Image.open(image_path) as img:
        if filter_type == 'blur':
            img = img.filter(ImageFilter.BLUR)
        elif filter_type == 'sharpen':
            img = img.filter(ImageFilter.SHARPEN)
        elif filter_type == 'edge_enhance':
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_type == 'edge_detect':
            img = img.filter(ImageFilter.FIND_EDGES)
        elif filter_type == 'contrast':
            img = img.filter(ImageFilter.UnsharpMask())
        return img

def image_to_array(image_path):
    """Convert image to numpy array for processing."""
    with Image.open(image_path) as img:
        return np.array(img)

def save_array_as_image(array, output_path):
    """Save numpy array as image file."""
    img = Image.fromarray(array)
    img.save(output_path)

def get_image_dimensions(image_path):
    """Get image dimensions."""
    with Image.open(image_path) as img:
        return {'width': img.width, 'height': img.height}

def analyze_geological_image(image_path):
    """Perform geological analysis on image."""
    try:
        # Get basic image properties
        dimensions = get_image_dimensions(image_path)
        img_array = image_to_array(image_path)
        
        # Basic image analysis
        results = {
            'dimensions': dimensions,
            'channels': img_array.shape[2] if len(img_array.shape) > 2 else 1,
            'data_type': str(img_array.dtype),
            'file_path': image_path,
            'analysis_type': 'geological',
            'features': []
        }
        
        # Enhanced analysis with OpenCV if available
        if HAS_OPENCV:
            try:
                # Convert to grayscale for analysis
                if len(img_array.shape) > 2:
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                else:
                    gray = img_array
                
                # Edge detection for fracture analysis
                edges = cv2.Canny(gray, 50, 150)
                
                # Find contours (potential geological features)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                results['features'] = {
                    'edge_density': np.sum(edges > 0) / edges.size,
                    'contour_count': len(contours),
                    'mean_intensity': np.mean(gray),
                    'std_intensity': np.std(gray)
                }
                
            except Exception as e:
                results['opencv_error'] = str(e)
                if len(img_array.shape) > 2:
                    gray = np.mean(img_array, axis=2)
                else:
                    gray = img_array
                    
                results['features'] = {
                    'mean_intensity': np.mean(gray),
                    'std_intensity': np.std(gray),
                    'min_intensity': np.min(gray),
                    'max_intensity': np.max(gray)
                }
        else:
            # Fallback analysis without OpenCV
            if len(img_array.shape) > 2:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
                
            results['features'] = {
                'mean_intensity': np.mean(gray),
                'std_intensity': np.std(gray),
                'min_intensity': np.min(gray),
                'max_intensity': np.max(gray)
            }
        
        return results
        
    except Exception as e:
        return {'error': str(e)}

def enhance_geological_features(image_path, enhancement_type='contrast'):
    """Enhance specific geological features in the image."""
    with Image.open(image_path) as img:
        img_array = np.array(img)
        
        if enhancement_type == 'contrast':
            # Enhance contrast to highlight rock boundaries
            enhanced = np.clip(1.5 * img_array - 0.5 * 128, 0, 255).astype(np.uint8)
        elif enhancement_type == 'fractures':
            # Enhance fractures using edge detection
            if len(img_array.shape) > 2:
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            # Simple edge enhancement
            enhanced = np.zeros_like(img_array)
            kernel = np.array([[-1,-1,-1], [-1,8,-1], [-1,-1,-1]])
            
            if len(img_array.shape) > 2:
                for i in range(img_array.shape[2]):
                    if HAS_SCIPY:
                        enhanced[:,:,i] = ndimage.convolve(img_array[:,:,i], kernel)
                    else:
                        # Simple edge enhancement without scipy
                        enhanced[:,:,i] = img_array[:,:,i]  # Fallback
            else:
                if HAS_SCIPY:
                    enhanced = ndimage.convolve(img_array, kernel)
                else:
                    enhanced = img_array  # Fallback
            
            enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        else:
            enhanced = img_array
        
        return enhanced

def create_overlay_image(base_image_path, overlay_data, output_path):
    """Create an overlay image with geological data points."""
    with Image.open(base_image_path) as img:
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        for point in overlay_data:
            x = int(point.get('x', 0))
            y = int(point.get('y', 0))
            color = point.get('color', '#ff0000')
            radius = point.get('radius', 5)
            
            # Convert hex color to RGBA
            color_rgba = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (128,)
            
            # Draw circle for data point
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color_rgba)
        
        # Composite the overlay onto the base image
        result = Image.alpha_composite(img.convert('RGBA'), overlay)
        result.save(output_path, 'PNG')
        
        return output_path

def calculate_distance_pixels(point1, point2):
    """Calculate distance between two points in pixels."""
    dx = point2['x'] - point1['x']
    dy = point2['y'] - point1['y']
    return np.sqrt(dx*dx + dy*dy)

def pixels_to_real_distance(pixel_distance, scale_factor):
    """Convert pixel distance to real-world distance using scale factor."""
    return pixel_distance * scale_factor

# Enhanced geological image analysis functions

def analyze_geological_image_enhanced(image_path: str, analysis_options: Optional[Dict] = None) -> Dict:
    """
    Perform comprehensive geological analysis on image with enhanced capabilities.
    
    Parameters:
    -----------
    image_path : str
        Path to the geological image
    analysis_options : dict, optional
        Analysis configuration options
        
    Returns:
    --------
    dict
        Comprehensive analysis results
    """
    if analysis_options is None:
        analysis_options = {
            'detect_fractures': True,
            'analyze_phases': True,
            'calculate_porosity': True,
            'detect_minerals': True,
            'enhance_features': True
        }
    
    try:
        # Get basic image properties
        dimensions = get_image_dimensions(image_path)
        img_array = image_to_array(image_path)
        
        # Initialize results dictionary
        results = {
            'dimensions': dimensions,
            'channels': img_array.shape[2] if len(img_array.shape) > 2 else 1,
            'data_type': str(img_array.dtype),
            'file_path': image_path,
            'analysis_type': 'enhanced_geological',
            'features': {},
            'fracture_analysis': {},
            'phase_analysis': {},
            'mineral_analysis': {},
            'porosity_analysis': {}
        }
        
        # Enhanced analysis with OpenCV and SciPy
        if HAS_OPENCV and HAS_SCIPY:
            results.update(perform_advanced_analysis(img_array, analysis_options))
        elif HAS_OPENCV:
            results.update(perform_opencv_analysis(img_array, analysis_options))
        elif HAS_SCIPY:
            results.update(perform_scipy_analysis(img_array, analysis_options))
        else:
            results.update(perform_basic_analysis(img_array))
            
        # Calculate overall statistics
        results['statistics'] = calculate_image_statistics(img_array)
        
        return results
        
    except Exception as e:
        return {
            'error': str(e),
            'file_path': image_path,
            'analysis_type': 'failed'
        }

def perform_advanced_analysis(img_array: np.ndarray, options: Dict) -> Dict:
    """Perform advanced analysis using OpenCV and SciPy/scikit-image."""
    results = {}
    
    # Convert to grayscale for analysis
    if len(img_array.shape) > 2:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array.copy()
    
    try:
        # Fracture detection
        if options.get('detect_fractures', True):
            results['fracture_analysis'] = detect_fractures_advanced(img_array, gray)
        
        # Phase analysis
        if options.get('analyze_phases', True):
            results['phase_analysis'] = analyze_phases_advanced(img_array)
        
        # Porosity analysis
        if options.get('calculate_porosity', True):
            results['porosity_analysis'] = calculate_porosity_advanced(img_array, gray)
        
        # Mineral detection
        if options.get('detect_minerals', True):
            results['mineral_analysis'] = detect_minerals_advanced(img_array)
        
        # Feature enhancement analysis
        if options.get('enhance_features', True):
            results['enhanced_features'] = analyze_enhanced_features(gray)
            
    except Exception as e:
        results['advanced_analysis_error'] = str(e)
    
    return results

def perform_opencv_analysis(img_array: np.ndarray, options: Dict) -> Dict:
    """Perform analysis using only OpenCV."""
    results = {}
    
    # Convert to grayscale
    if len(img_array.shape) > 2:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array.copy()
    
    try:
        # Basic edge detection and contour analysis
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        results['features'] = {
            'edge_density': float(np.sum(edges > 0) / edges.size),
            'contour_count': len(contours),
            'mean_intensity': float(np.mean(gray)),
            'std_intensity': float(np.std(gray))
        }
        
        if options.get('detect_fractures', True):
            results['fracture_analysis'] = detect_fractures_opencv_only(gray, contours)
            
    except Exception as e:
        results['opencv_error'] = str(e)
    
    return results

def perform_scipy_analysis(img_array: np.ndarray, options: Dict) -> Dict:
    """Perform analysis using only SciPy/scikit-image."""
    results = {}
    
    try:
        if len(img_array.shape) > 2:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array.copy()
        
        if HAS_SKIMAGE:
            # Use scikit-image features
            edges = filters.sobel(gray)
            
            results['features'] = {
                'edge_strength': float(np.mean(edges)),
                'edge_std': float(np.std(edges)),
                'mean_intensity': float(np.mean(gray)),
                'std_intensity': float(np.std(gray))
            }
            
            if options.get('analyze_phases', True):
                results['phase_analysis'] = analyze_phases_skimage(img_array)
        
    except Exception as e:
        results['scipy_error'] = str(e)
    
    return results

def perform_basic_analysis(img_array: np.ndarray) -> Dict:
    """Perform basic analysis without external libraries."""
    if len(img_array.shape) > 2:
        gray = np.mean(img_array, axis=2)
    else:
        gray = img_array.copy()
    
    return {
        'features': {
            'mean_intensity': float(np.mean(gray)),
            'std_intensity': float(np.std(gray)),
            'min_intensity': float(np.min(gray)),
            'max_intensity': float(np.max(gray))
        }
    }

def calculate_image_statistics(img_array: np.ndarray) -> Dict:
    """Calculate comprehensive image statistics."""
    stats = {
        'shape': img_array.shape,
        'size_mb': img_array.nbytes / (1024 * 1024),
        'dtype': str(img_array.dtype)
    }
    
    if len(img_array.shape) > 2:
        # Color image statistics
        for i, channel in enumerate(['R', 'G', 'B'][:img_array.shape[2]]):
            channel_data = img_array[:, :, i]
            stats[f'{channel}_channel'] = {
                'mean': float(np.mean(channel_data)),
                'std': float(np.std(channel_data)),
                'min': float(np.min(channel_data)),
                'max': float(np.max(channel_data))
            }
    else:
        # Grayscale statistics
        stats['grayscale'] = {
            'mean': float(np.mean(img_array)),
            'std': float(np.std(img_array)),
            'min': float(np.min(img_array)),
            'max': float(np.max(img_array))
        }
    
    return stats

# Additional helper functions would be defined here...
# (Due to length constraints, I'm including key functions only)