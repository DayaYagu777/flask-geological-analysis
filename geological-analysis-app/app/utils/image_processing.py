from PIL import Image, ImageFilter, ImageDraw
import numpy as np

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from scipy import ndimage
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

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