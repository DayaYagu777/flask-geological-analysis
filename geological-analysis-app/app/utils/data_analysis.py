from openpyxl import load_workbook
import pandas as pd
import numpy as np

def load_excel_data(file_path):
    """Load data from an Excel file."""
    try:
        # Try to load with pandas first for better header handling
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"Error loading Excel file with pandas: {e}")
        try:
            # Fallback to openpyxl
            workbook = load_workbook(filename=file_path)
            sheet = workbook.active
            data = pd.DataFrame(sheet.values)
            return data
        except Exception as e2:
            print(f"Error loading Excel file with openpyxl: {e2}")
            return None

def analyze_data(data):
    """Perform basic data analysis on the loaded data."""
    if data is None:
        return None
    
    # Example analysis: calculate mean and standard deviation
    analysis_results = {
        'mean': data.mean().to_dict() if hasattr(data.mean(), 'to_dict') else str(data.mean()),
        'std_dev': data.std().to_dict() if hasattr(data.std(), 'to_dict') else str(data.std()),
        'count': len(data),
        'columns': data.columns.tolist()
    }
    return analysis_results

def filter_data(data, column_name, threshold):
    """Filter data based on a threshold for a specific column."""
    if column_name in data.columns:
        filtered_data = data[data[column_name] > threshold]
        return filtered_data
    else:
        print(f"Column {column_name} does not exist in the data.")
        return None

def filter_geological_data(data, filters):
    """Filter geological data based on multiple criteria."""
    if not data:
        return []
    
    df = pd.DataFrame(data)
    filtered_df = df.copy()
    
    for filter_key, filter_value in filters.items():
        if filter_key in df.columns and filter_value is not None:
            if isinstance(filter_value, dict):
                # Range filter
                if 'min' in filter_value and filter_value['min'] is not None:
                    filtered_df = filtered_df[filtered_df[filter_key] >= filter_value['min']]
                if 'max' in filter_value and filter_value['max'] is not None:
                    filtered_df = filtered_df[filtered_df[filter_key] <= filter_value['max']]
            else:
                # Exact match filter
                filtered_df = filtered_df[filtered_df[filter_key] == filter_value]
    
    return filtered_df.to_dict('records')

def analyze_rmr_data(data, filters):
    """Analyze RMR (Rock Mass Rating) data with geological criteria."""
    if not data:
        return []
    
    df = pd.DataFrame(data)
    
    # Apply filters
    filtered_data = filter_geological_data(data, filters)
    filtered_df = pd.DataFrame(filtered_data)
    
    if filtered_df.empty:
        return []
    
    # Calculate RMR coordinates and colors based on rating
    rmr_data = []
    for _, row in filtered_df.iterrows():
        rmr_value = row.get('RMR', 0) if 'RMR' in row else 0
        
        # Determine color based on RMR value
        if rmr_value >= 80:
            color = '#00ff00'  # Green - Very good rock
            class_name = 'Muy Buena'
        elif rmr_value >= 60:
            color = '#80ff00'  # Light green - Good rock
            class_name = 'Buena'
        elif rmr_value >= 40:
            color = '#ffff00'  # Yellow - Fair rock
            class_name = 'Regular'
        elif rmr_value >= 20:
            color = '#ff8000'  # Orange - Poor rock
            class_name = 'Mala'
        else:
            color = '#ff0000'  # Red - Very poor rock
            class_name = 'Muy Mala'
        
        rmr_record = row.to_dict()
        rmr_record.update({
            'color': color,
            'class': class_name,
            'x': row.get('X', 0),
            'y': row.get('Y', 0),
            'rmr_value': rmr_value
        })
        rmr_data.append(rmr_record)
    
    return rmr_data

def analyze_fracture_data(data, filters):
    """Analyze fracture data for structural geology visualization."""
    if not data:
        return []
    
    df = pd.DataFrame(data)
    
    # Apply filters
    filtered_data = filter_geological_data(data, filters)
    filtered_df = pd.DataFrame(filtered_data)
    
    if filtered_df.empty:
        return []
    
    # Group fractures by family and assign colors
    fracture_families = {}
    family_colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
    
    fracture_data = []
    for _, row in filtered_df.iterrows():
        family = row.get('Familia', 'Unknown')
        if family not in fracture_families:
            color_index = len(fracture_families) % len(family_colors)
            fracture_families[family] = family_colors[color_index]
        
        fracture_record = row.to_dict()
        fracture_record.update({
            'color': fracture_families[family],
            'family': family,
            'dip': row.get('Buzamiento', 0),
            'dip_direction': row.get('Direccion_Buzamiento', 0),
            'x': row.get('X', 0),
            'y': row.get('Y', 0)
        })
        fracture_data.append(fracture_record)
    
    return fracture_data

def calculate_excavation_coordinates(data, image_dimensions, scale_factor=1.0):
    """Calculate coordinates for plotting on image based on PK and frente data."""
    coordinates = []
    
    for record in data:
        pk = record.get('PK_medio', 0)
        frente = record.get('Frente', 0)
        
        # Convert geological coordinates to image pixels
        # This is a simplified conversion - in reality, you'd need proper coordinate transformation
        x = int((pk * scale_factor) % image_dimensions['width'])
        y = int((frente * scale_factor) % image_dimensions['height'])
        
        record['image_x'] = x
        record['image_y'] = y
        coordinates.append(record)
    
    return coordinates

def generate_visualization(data):
    """Generate visualizations based on the analyzed data."""
    # Placeholder for visualization logic
    # This could involve creating plots using libraries like matplotlib or seaborn
    visualization_data = {
        'charts': [],
        'statistics': {},
        'recommendations': []
    }
    
    if data:
        df = pd.DataFrame(data)
        visualization_data['statistics'] = {
            'total_records': len(df),
            'columns': df.columns.tolist(),
            'summary': df.describe().to_dict() if len(df) > 0 else {}
        }
    
    return visualization_data