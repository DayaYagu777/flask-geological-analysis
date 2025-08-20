import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, RadioButtons, CheckButtons
from typing import List, Dict, Tuple, Optional
try:
    import mplstereonet
    HAS_MPLSTEREONET = True
except ImportError:
    HAS_MPLSTEREONET = False
    print("mplstereonet not available - using simplified stereonet plotting")

def plot_stereonet(data: List[Tuple[float, float]], title: str = 'Stereonet Plot', 
                   families: Optional[List[str]] = None) -> plt.Figure:
    """
    Create an enhanced stereonet plot from the given data.

    Parameters:
    -----------
    data : List[Tuple[float, float]]
        List of tuples containing (dip, dip_direction) of geological features
    title : str
        Title of the plot
    families : List[str], optional
        Fracture families for color coding
        
    Returns:
    --------
    matplotlib.figure.Figure
        Stereonet figure
    """
    if HAS_MPLSTEREONET:
        return plot_enhanced_stereonet(data, title, families)
    else:
        return plot_basic_stereonet(data, title, families)

def plot_enhanced_stereonet(data: List[Tuple[float, float]], title: str,
                          families: Optional[List[str]] = None) -> plt.Figure:
    """Plot using mplstereonet library for accurate stereonet projections."""
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='stereonet'))
    
    # Separate data by families if provided
    if families:
        unique_families = list(set(families))
        colors = plt.cm.Set1(np.linspace(0, 1, len(unique_families)))
        
        for i, family in enumerate(unique_families):
            family_data = [data[j] for j, f in enumerate(families) if f == family]
            if family_data:
                dips, dip_dirs = zip(*family_data)
                ax.pole(dip_dirs, dips, marker='o', markersize=6, 
                       color=colors[i], label=f'Family {family}')
    else:
        dips, dip_dirs = zip(*data) if data else ([], [])
        ax.pole(dip_dirs, dips, marker='o', markersize=6, color='blue')
    
    # Add great circles for major orientations if enough data
    if len(data) > 5:
        # Calculate mean orientation and plot great circle
        dips, dip_dirs = zip(*data)
        mean_dip_dir = np.degrees(np.arctan2(np.mean(np.sin(np.radians(dip_dirs))),
                                           np.mean(np.cos(np.radians(dip_dirs))))) % 360
        mean_dip = np.mean(dips)
        ax.plane(mean_dip_dir, mean_dip, color='red', linewidth=2, alpha=0.7, 
                label='Mean Orientation')
    
    ax.set_title(title, fontsize=14)
    ax.grid(True)
    
    if families:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    return fig

def plot_basic_stereonet(data: List[Tuple[float, float]], title: str,
                        families: Optional[List[str]] = None) -> plt.Figure:
    """Basic stereonet plot without mplstereonet."""
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='polar')
    
    # Configure polar plot to look like stereonet
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 90)
    ax.set_yticks(np.arange(0, 91, 15))
    ax.set_yticklabels([f'{90-y}°' for y in np.arange(0, 91, 15)])
    
    # Plot data points
    if families:
        unique_families = list(set(families))
        colors = plt.cm.Set1(np.linspace(0, 1, len(unique_families)))
        
        for i, family in enumerate(unique_families):
            family_data = [data[j] for j, f in enumerate(families) if f == family]
            if family_data:
                dips, dip_dirs = zip(*family_data)
                # Convert to polar coordinates (simplified projection)
                theta = np.radians(dip_dirs)
                r = dips
                ax.scatter(theta, r, c=[colors[i]], s=50, alpha=0.7, 
                          label=f'Family {family}')
    else:
        if data:
            dips, dip_dirs = zip(*data)
            theta = np.radians(dip_dirs)
            ax.scatter(theta, dips, c='blue', s=50, alpha=0.7)
    
    ax.set_title(title, pad=20, fontsize=14)
    
    if families:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    return fig

def create_interactive_stereonet(data: List[Tuple[float, float]], 
                               families: Optional[List[str]] = None) -> plt.Figure:
    """
    Create interactive stereonet with family filtering and contour controls.
    
    Parameters:
    -----------
    data : List[Tuple[float, float]]
        Fracture orientation data
    families : List[str], optional
        Fracture family labels
        
    Returns:
    --------
    matplotlib.figure.Figure
        Interactive stereonet figure
    """
    fig = plt.figure(figsize=(14, 10))
    
    # Main stereonet plot
    if HAS_MPLSTEREONET:
        ax = fig.add_subplot(111, projection='stereonet')
        ax.set_position([0.1, 0.1, 0.65, 0.8])
    else:
        ax = fig.add_subplot(111, projection='polar')
        ax.set_position([0.1, 0.1, 0.65, 0.8])
        setup_basic_stereonet(ax)
    
    # Initial plot
    plot_all_data(ax, data, families)
    
    # Control panel
    if families:
        unique_families = list(set(families))
        
        # Family selection checkboxes
        ax_check = plt.axes([0.8, 0.5, 0.15, 0.3])
        family_labels = unique_families
        initial_state = [True] * len(family_labels)
        check = CheckButtons(ax_check, family_labels, initial_state)
        
        # Update function for family selection
        def update_families(label):
            # Get current checkbox states
            active_families = [family_labels[i] for i, state in 
                             enumerate(check.get_status()) if state]
            
            # Filter data
            if active_families:
                filtered_data = []
                filtered_families = []
                for i, family in enumerate(families):
                    if family in active_families:
                        filtered_data.append(data[i])
                        filtered_families.append(family)
            else:
                filtered_data = data
                filtered_families = families
            
            # Clear and replot
            ax.clear()
            if HAS_MPLSTEREONET:
                pass  # mplstereonet handles clearing differently
            else:
                setup_basic_stereonet(ax)
            
            plot_all_data(ax, filtered_data, filtered_families)
            fig.canvas.draw()
        
        check.on_clicked(update_families)
    
    # Contour density control
    ax_density = plt.axes([0.8, 0.3, 0.15, 0.03])
    density_slider = Slider(ax_density, 'Contours', 0, 10, valinit=0, valfmt='%d')
    
    def update_density(val):
        # Add contour functionality if using mplstereonet
        if HAS_MPLSTEREONET and val > 0:
            try:
                dips, dip_dirs = zip(*data) if data else ([], [])
                if len(dips) > 10:
                    ax.density_contour(dip_dirs, dips, 
                                     levels=int(val), alpha=0.5, colors='red')
                    fig.canvas.draw()
            except Exception as e:
                print(f"Error adding contours: {e}")
    
    density_slider.on_changed(update_density)
    
    return fig

def setup_basic_stereonet(ax):
    """Setup basic polar plot to look like stereonet."""
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 90)
    ax.set_yticks(np.arange(0, 91, 15))
    ax.set_yticklabels([f'{90-y}°' for y in np.arange(0, 91, 15)])
    ax.grid(True)

def plot_all_data(ax, data: List[Tuple[float, float]], 
                  families: Optional[List[str]] = None):
    """Plot all data on the stereonet axes."""
    if not data:
        return
    
    if HAS_MPLSTEREONET:
        plot_enhanced_data(ax, data, families)
    else:
        plot_basic_data(ax, data, families)

def plot_enhanced_data(ax, data: List[Tuple[float, float]], 
                      families: Optional[List[str]] = None):
    """Plot data using mplstereonet."""
    if families:
        unique_families = list(set(families))
        colors = plt.cm.Set1(np.linspace(0, 1, len(unique_families)))
        
        for i, family in enumerate(unique_families):
            family_data = [data[j] for j, f in enumerate(families) if f == family]
            if family_data:
                dips, dip_dirs = zip(*family_data)
                ax.pole(dip_dirs, dips, marker='o', markersize=6, 
                       color=colors[i], label=f'Family {family}')
    else:
        dips, dip_dirs = zip(*data)
        ax.pole(dip_dirs, dips, marker='o', markersize=6, color='blue')

def plot_basic_data(ax, data: List[Tuple[float, float]], 
                   families: Optional[List[str]] = None):
    """Plot data on basic polar axes."""
    if families:
        unique_families = list(set(families))
        colors = plt.cm.Set1(np.linspace(0, 1, len(unique_families)))
        
        for i, family in enumerate(unique_families):
            family_data = [data[j] for j, f in enumerate(families) if f == family]
            if family_data:
                dips, dip_dirs = zip(*family_data)
                theta = np.radians(dip_dirs)
                ax.scatter(theta, dips, c=[colors[i]], s=50, alpha=0.7, 
                          label=f'Family {family}')
    else:
        dips, dip_dirs = zip(*data)
        theta = np.radians(dip_dirs)
        ax.scatter(theta, dips, c='blue', s=50, alpha=0.7)

def generate_stereonet_data(features: List[Dict]) -> List[Tuple[float, float]]:
    """
    Generate stereonet data from geological features with enhanced validation.

    Parameters:
    -----------
    features : List[Dict]
        List of geological features with dip and dip_direction

    Returns:
    --------
    List[Tuple[float, float]]
        List of (dip, dip_direction) tuples
    """
    data = []
    for feature in features:
        try:
            dip = float(feature.get('dip', feature.get('plunge', 0)))
            dip_dir = float(feature.get('dip_direction', feature.get('azimuth', 0)))
            
            # Validate ranges
            if 0 <= dip <= 90 and 0 <= dip_dir <= 360:
                data.append((dip, dip_dir))
            else:
                print(f"Invalid orientation data: dip={dip}, dip_dir={dip_dir}")
        except (ValueError, TypeError) as e:
            print(f"Error processing feature {feature}: {e}")
    
    return data

def calculate_orientation_statistics(data: List[Tuple[float, float]]) -> Dict:
    """
    Calculate statistical parameters for orientation data.
    
    Parameters:
    -----------
    data : List[Tuple[float, float]]
        Orientation data as (dip, dip_direction) tuples
        
    Returns:
    --------
    Dict
        Statistical parameters
    """
    if not data:
        return {}
    
    dips, dip_dirs = zip(*data)
    
    # Convert to arrays
    dips = np.array(dips)
    dip_dirs = np.array(dip_dirs)
    
    # Circular statistics for dip direction
    dip_dirs_rad = np.radians(dip_dirs)
    mean_x = np.mean(np.cos(dip_dirs_rad))
    mean_y = np.mean(np.sin(dip_dirs_rad))
    mean_dip_dir = np.degrees(np.arctan2(mean_y, mean_x)) % 360
    
    # Concentration parameter
    R = np.sqrt(mean_x**2 + mean_y**2)
    
    statistics = {
        'count': len(data),
        'mean_dip': float(np.mean(dips)),
        'std_dip': float(np.std(dips)),
        'mean_dip_direction': float(mean_dip_dir),
        'concentration': float(R),
        'dispersion': float(1 - R),
        'dip_range': [float(np.min(dips)), float(np.max(dips))],
        'dip_dir_range': [float(np.min(dip_dirs)), float(np.max(dip_dirs))]
    }
    
    return statistics