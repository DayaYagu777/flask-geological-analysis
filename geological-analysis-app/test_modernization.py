"""
Test suite for modernized geological analysis system.
Validates that all original functionality is preserved while testing new features.
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
import os
import json
from typing import Dict, List
from unittest.mock import Mock, patch

# Import modules to test
try:
    from app.utils.data_analysis import (
        load_excel_data, analyze_rmr_data, analyze_fracture_data,
        clean_geological_data, generate_visualization,
        calculate_rmr_statistics, calculate_fracture_statistics
    )
    from app.utils.image_processing import (
        analyze_geological_image, get_image_dimensions,
        analyze_geological_image_enhanced, calculate_image_statistics
    )
    from app.utils.stereonet import (
        plot_stereonet, generate_stereonet_data,
        calculate_orientation_statistics
    )
except ImportError as e:
    pytest.skip(f"Could not import modules: {e}", allow_module_level=True)

class TestDataAnalysisPreservation:
    """Test that original data analysis functionality is preserved."""
    
    @pytest.fixture
    def sample_geological_data(self):
        """Create sample geological data matching original format."""
        return pd.DataFrame({
            'Frente': ['T1', 'T1', 'T2', 'T2', 'T3'],
            'PK_medio': [100.5, 101.2, 200.3, 201.1, 300.7],
            'RMR': [75, 68, 45, 52, 91],
            'Familia': ['F1', 'F1', 'F2', 'F3', 'F1'],
            'Buzamiento': [45, 50, 60, 75, 25],
            'Direccion_Buzamiento': [120, 125, 180, 200, 110],
            'X': [150, 180, 300, 320, 400],
            'Y': [200, 220, 350, 370, 450]
        })
    
    def test_rmr_classification_preserved(self, sample_geological_data):
        """Test that RMR classification colors are preserved exactly."""
        data_records = sample_geological_data.to_dict('records')
        rmr_results = analyze_rmr_data(data_records, {})
        
        # Verify original color classification is preserved
        color_mapping = {}
        for record in rmr_results:
            rmr_value = record.get('rmr_value', record.get('RMR', 0))
            color = record.get('color')
            
            if rmr_value >= 80:
                assert color == '#00ff00', f"RMR {rmr_value} should be green"
            elif rmr_value >= 60:
                assert color == '#80ff00', f"RMR {rmr_value} should be light green"
            elif rmr_value >= 40:
                assert color == '#ffff00', f"RMR {rmr_value} should be yellow"
            elif rmr_value >= 20:
                assert color == '#ff8000', f"RMR {rmr_value} should be orange"
            else:
                assert color == '#ff0000', f"RMR {rmr_value} should be red"
    
    def test_fracture_family_filtering(self, sample_geological_data):
        """Test that fracture family filtering works as originally."""
        data_records = sample_geological_data.to_dict('records')
        
        # Test filtering by specific family
        filters = {'Familia': 'F1'}
        fracture_results = analyze_fracture_data(data_records, filters)
        
        # Should only contain F1 family fractures
        f1_records = [r for r in fracture_results if r.get('family') == 'F1']
        assert len(f1_records) == 2, "Should find 2 F1 family fractures"
        
        # Verify original data is preserved
        for record in f1_records:
            assert record.get('family') == 'F1'
            assert 'color' in record, "Color assignment should be present"
            assert 'x' in record and 'y' in record, "Coordinates should be preserved"
    
    def test_pk_range_filtering(self, sample_geological_data):
        """Test PK medio range filtering preserves original behavior."""
        data_records = sample_geological_data.to_dict('records')
        
        # Test PK range filtering
        filters = {'PK_medio': {'min': 150, 'max': 250}}
        rmr_results = analyze_rmr_data(data_records, filters)
        
        # Should only contain records within PK range
        for record in rmr_results:
            pk_value = record.get('PK_medio', 0)
            assert 150 <= pk_value <= 250, f"PK {pk_value} outside expected range"
    
    def test_coordinate_assignment_preserved(self, sample_geological_data):
        """Test that coordinate assignment logic is preserved."""
        data_records = sample_geological_data.to_dict('records')
        rmr_results = analyze_rmr_data(data_records, {})
        
        # Verify coordinates are properly assigned
        for i, record in enumerate(rmr_results):
            expected_x = sample_geological_data.iloc[i]['X']
            expected_y = sample_geological_data.iloc[i]['Y']
            
            assert record.get('x') == expected_x, "X coordinate should match original"
            assert record.get('y') == expected_y, "Y coordinate should match original"

class TestDataAnalysisEnhancements:
    """Test new enhanced data analysis features."""
    
    @pytest.fixture
    def sample_data_with_issues(self):
        """Create data with common issues for testing cleaning."""
        return pd.DataFrame({
            'Frente': ['T1', ' T2 ', 'T3', '', 'T1'],
            'PK_medio': [100.5, 'invalid', 200.3, 201.1, 300.7],
            'RMR': [75, 68, 150, -10, 91],  # Out of range values
            'Buzamiento': [45, 50, 100, -5, 25],  # Out of range
            'Direccion_Buzamiento': [120, 125, 380, -10, 110]  # Out of range
        })
    
    def test_data_cleaning_preserves_valid_data(self, sample_data_with_issues):
        """Test that data cleaning preserves valid data while fixing issues."""
        cleaned_df = clean_geological_data(sample_data_with_issues)
        
        # Check RMR is clipped to valid range
        assert cleaned_df['RMR'].min() >= 0, "RMR should be >= 0"
        assert cleaned_df['RMR'].max() <= 100, "RMR should be <= 100"
        
        # Check buzamiento is clipped to valid range
        assert cleaned_df['Buzamiento'].min() >= 0, "Buzamiento should be >= 0"
        assert cleaned_df['Buzamiento'].max() <= 90, "Buzamiento should be <= 90"
        
        # Check direction is normalized to 0-360
        assert cleaned_df['Direccion_Buzamiento'].min() >= 0, "Direction should be >= 0"
        assert cleaned_df['Direccion_Buzamiento'].max() < 360, "Direction should be < 360"
    
    def test_rmr_statistics_calculation(self):
        """Test enhanced RMR statistics calculation."""
        df = pd.DataFrame({
            'RMR': [75, 68, 45, 52, 91, 35, 80, 22, 88, 15]
        })
        
        stats = calculate_rmr_statistics(df)
        
        # Verify basic statistics
        assert 'mean' in stats
        assert 'std' in stats
        assert 'percentiles' in stats
        assert 'classification_distribution' in stats
        
        # Verify classification counts
        classifications = stats['classification_distribution']
        assert 'Very Good' in classifications or 'Good' in classifications
        assert isinstance(classifications, dict)
    
    def test_fracture_statistics_calculation(self):
        """Test enhanced fracture statistics."""
        df = pd.DataFrame({
            'Familia': ['F1', 'F1', 'F2', 'F2', 'F3'],
            'Buzamiento': [45, 50, 60, 75, 25],
            'Direccion_Buzamiento': [120, 125, 180, 185, 110]
        })
        
        stats = calculate_fracture_statistics(df)
        
        # Verify family distribution
        assert 'family_distribution' in stats
        assert 'F1' in stats['family_distribution']
        assert 'F2' in stats['family_distribution']
        
        # Verify dip statistics
        if 'dip' in stats:
            assert 'mean' in stats['dip']
            assert 'dominant_range' in stats['dip']

class TestImageProcessingPreservation:
    """Test that image processing functionality is preserved."""
    
    @pytest.fixture
    def sample_image_array(self):
        """Create a sample image array for testing."""
        # Create a simple 100x100x3 RGB image
        return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    def test_image_dimensions_preserved(self, sample_image_array):
        """Test that image dimension calculation is preserved."""
        # Create temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            from PIL import Image
            img = Image.fromarray(sample_image_array)
            img.save(tmp_file.name)
            
            try:
                dimensions = get_image_dimensions(tmp_file.name)
                assert dimensions['width'] == 100
                assert dimensions['height'] == 100
            finally:
                os.unlink(tmp_file.name)
    
    @patch('app.utils.image_processing.HAS_OPENCV', True)
    def test_basic_analysis_preserved(self, sample_image_array):
        """Test that basic geological analysis is preserved."""
        # Mock OpenCV functions for testing
        with patch('cv2.cvtColor') as mock_cvt, \
             patch('cv2.Canny') as mock_canny, \
             patch('cv2.findContours') as mock_contours:
            
            mock_cvt.return_value = np.mean(sample_image_array, axis=2).astype(np.uint8)
            mock_canny.return_value = np.zeros((100, 100), dtype=np.uint8)
            mock_contours.return_value = ([], None)
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                from PIL import Image
                img = Image.fromarray(sample_image_array)
                img.save(tmp_file.name)
                
                try:
                    results = analyze_geological_image(tmp_file.name)
                    
                    # Verify basic structure is preserved
                    assert 'dimensions' in results
                    assert 'channels' in results
                    assert 'analysis_type' in results
                    assert results['analysis_type'] == 'geological'
                    
                finally:
                    os.unlink(tmp_file.name)

class TestStereonetPreservation:
    """Test that stereonet functionality is preserved and enhanced."""
    
    def test_stereonet_data_generation_preserved(self):
        """Test that stereonet data generation preserves original format."""
        features = [
            {'dip': 45, 'dip_direction': 120},
            {'dip': 50, 'dip_direction': 125},
            {'dip': 60, 'dip_direction': 180}
        ]
        
        # Test with new field names (should work)
        data = generate_stereonet_data(features)
        assert len(data) == 3
        assert data[0] == (45, 120)
        
        # Test with legacy field names (should also work)
        legacy_features = [
            {'plunge': 45, 'azimuth': 120},
            {'plunge': 50, 'azimuth': 125}
        ]
        legacy_data = generate_stereonet_data(legacy_features)
        assert len(legacy_data) == 2
        assert legacy_data[0] == (45, 120)
    
    def test_orientation_statistics_calculation(self):
        """Test new orientation statistics functionality."""
        data = [(45, 120), (50, 125), (60, 180), (35, 115)]
        
        stats = calculate_orientation_statistics(data)
        
        # Verify statistical parameters
        assert 'count' in stats
        assert 'mean_dip' in stats
        assert 'mean_dip_direction' in stats
        assert 'concentration' in stats
        assert 'dispersion' in stats
        
        assert stats['count'] == 4
        assert 0 <= stats['concentration'] <= 1
        assert 0 <= stats['dispersion'] <= 1

class TestAPICompatibility:
    """Test API endpoint compatibility."""
    
    def test_filter_data_response_format(self):
        """Test that filter data maintains expected response format."""
        sample_data = [
            {'Frente': 'T1', 'PK_medio': 100.5, 'RMR': 75, 'X': 150, 'Y': 200},
            {'Frente': 'T2', 'PK_medio': 200.3, 'RMR': 45, 'X': 300, 'Y': 350}
        ]
        
        # Test RMR mode
        rmr_results = analyze_rmr_data(sample_data, {})
        
        # Verify response format matches original
        assert isinstance(rmr_results, list)
        for record in rmr_results:
            assert 'color' in record
            assert 'class' in record
            assert 'x' in record
            assert 'y' in record
            assert 'rmr_value' in record
        
        # Test fracture mode
        fracture_sample = [
            {'Familia': 'F1', 'Buzamiento': 45, 'Direccion_Buzamiento': 120, 'X': 150, 'Y': 200}
        ]
        fracture_results = analyze_fracture_data(fracture_sample, {})
        
        assert isinstance(fracture_results, list)
        for record in fracture_results:
            assert 'family' in record
            assert 'color' in record
            assert 'x' in record
            assert 'y' in record

class TestVisualizationEnhancements:
    """Test new visualization capabilities."""
    
    def test_visualization_data_generation(self):
        """Test comprehensive visualization data generation."""
        df = pd.DataFrame({
            'RMR': [75, 68, 45, 52, 91],
            'Familia': ['F1', 'F1', 'F2', 'F3', 'F1'],
            'X': [150, 180, 300, 320, 400],
            'Y': [200, 220, 350, 370, 450]
        })
        
        viz_data = generate_visualization(df)
        
        # Verify structure
        assert 'charts' in viz_data
        assert 'statistics' in viz_data
        assert 'recommendations' in viz_data
        
        # Verify statistics
        stats = viz_data['statistics']
        assert 'total_records' in stats
        assert stats['total_records'] == 5
        
        # Check for RMR-specific statistics
        if 'rmr' in stats:
            rmr_stats = stats['rmr']
            assert 'mean' in rmr_stats
            assert 'classification_distribution' in rmr_stats

class TestErrorHandling:
    """Test robust error handling."""
    
    def test_invalid_data_handling(self):
        """Test handling of invalid or missing data."""
        # Test with None data
        result = analyze_rmr_data(None, {})
        assert result == []
        
        # Test with empty data
        result = analyze_rmr_data([], {})
        assert result == []
        
        # Test with malformed data
        malformed_data = [{'invalid': 'data'}]
        result = analyze_rmr_data(malformed_data, {})
        # Should handle gracefully without crashing
        assert isinstance(result, list)
    
    def test_missing_file_handling(self):
        """Test handling of missing image files."""
        result = analyze_geological_image('nonexistent_file.jpg')
        assert 'error' in result
        assert result['analysis_type'] == 'failed'

# Integration test
class TestFullWorkflow:
    """Test complete geological analysis workflow."""
    
    def test_complete_rmr_workflow(self):
        """Test complete RMR analysis workflow from data to visualization."""
        # Step 1: Create sample data
        sample_data = pd.DataFrame({
            'Frente': ['T1', 'T1', 'T2'],
            'PK_medio': [100.5, 101.2, 200.3],
            'RMR': [75, 68, 45],
            'X': [150, 180, 300],
            'Y': [200, 220, 350]
        })
        
        # Step 2: Convert to records format
        data_records = sample_data.to_dict('records')
        
        # Step 3: Apply filters
        filters = {'PK_medio': {'min': 100, 'max': 200}}
        filtered_results = analyze_rmr_data(data_records, filters)
        
        # Step 4: Verify results
        assert len(filtered_results) == 2  # Should filter out T2 record
        
        # Step 5: Generate visualization
        viz_data = generate_visualization(sample_data)
        assert viz_data['statistics']['total_records'] == 3
        
        # Step 6: Verify recommendations
        recommendations = viz_data.get('recommendations', [])
        assert isinstance(recommendations, list)

if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])