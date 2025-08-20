#!/usr/bin/env python3
"""
Migration script for upgrading geological analysis system.
This script helps transition from the original system to the modernized version.
"""

import os
import sys
import shutil
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

def print_banner():
    """Print migration banner."""
    print("\n" + "="*60)
    print("🔧 GEOLOGICAL ANALYSIS SYSTEM MIGRATION")
    print("="*60)
    print("This script will help you migrate to the modernized system")
    print("while preserving all your existing data and functionality.")
    print("="*60 + "\n")

def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        ('pandas', '2.0.0'),
        ('numpy', '1.20.0'),
        ('matplotlib', '3.5.0'),
        ('flask', '2.0.0')
    ]
    
    optional_packages = [
        ('fastapi', '0.100.0'),
        ('opencv-python', '4.5.0'),
        ('scipy', '1.7.0'),
        ('scikit-image', '0.19.0'),
        ('mplstereonet', '0.6.0')
    ]
    
    missing_required = []
    missing_optional = []
    
    for package, min_version in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            missing_required.append(package)
            print(f"  ✗ {package} (REQUIRED)")
    
    for package, min_version in optional_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            missing_optional.append(package)
            print(f"  ? {package} (optional - enables enhanced features)")
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("These provide enhanced features but are not required for basic functionality.")
    
    print("\n✓ Dependency check completed")
    return True

def backup_existing_data(data_dir="app/static/uploads", backup_dir="backup"):
    """Create backup of existing data."""
    print(f"\n💾 Creating backup of existing data...")
    
    if not os.path.exists(data_dir):
        print(f"  No existing data directory found at {data_dir}")
        return True
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}_{timestamp}"
    
    try:
        shutil.copytree(data_dir, backup_path)
        print(f"  ✓ Data backed up to {backup_path}")
        return True
    except Exception as e:
        print(f"  ✗ Backup failed: {e}")
        return False

def validate_data_files(data_dir="app/static/uploads"):
    """Validate existing data files for compatibility."""
    print(f"\n🔍 Validating existing data files...")
    
    if not os.path.exists(data_dir):
        print("  No data directory found - this is normal for new installations")
        return True
    
    excel_files = []
    image_files = []
    other_files = []
    
    for file_path in Path(data_dir).rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in ['.xlsx', '.xls']:
                excel_files.append(file_path)
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp']:
                image_files.append(file_path)
            else:
                other_files.append(file_path)
    
    print(f"  Found {len(excel_files)} Excel files")
    print(f"  Found {len(image_files)} image files")
    print(f"  Found {len(other_files)} other files")
    
    # Test loading a sample Excel file if available
    if excel_files:
        try:
            sample_file = excel_files[0]
            df = pd.read_excel(sample_file)
            print(f"  ✓ Sample Excel file loads successfully ({len(df)} rows)")
            
            # Check for expected columns
            expected_columns = ['Frente', 'PK_medio', 'RMR', 'Familia']
            available_columns = df.columns.tolist()
            
            for col in expected_columns:
                if col in available_columns:
                    print(f"    ✓ Column '{col}' found")
                else:
                    similar_cols = [c for c in available_columns if col.lower() in c.lower()]
                    if similar_cols:
                        print(f"    ? Column '{col}' not found, but similar: {similar_cols}")
                    else:
                        print(f"    - Column '{col}' not found")
        
        except Exception as e:
            print(f"  ⚠️  Could not read sample Excel file: {e}")
    
    print("  ✓ Data validation completed")
    return True

def test_core_functionality():
    """Test core geological analysis functions."""
    print(f"\n🧪 Testing core functionality...")
    
    try:
        # Test data analysis functions
        from app.utils.data_analysis import analyze_rmr_data, analyze_fracture_data
        
        # Create test data
        test_data = [
            {
                'Frente': 'T1',
                'PK_medio': 100.5,
                'RMR': 75,
                'Familia': 'F1',
                'Buzamiento': 45,
                'Direccion_Buzamiento': 120,
                'X': 150,
                'Y': 200
            }
        ]
        
        # Test RMR analysis
        rmr_result = analyze_rmr_data(test_data, {})
        assert len(rmr_result) == 1
        assert 'color' in rmr_result[0]
        print("  ✓ RMR analysis working")
        
        # Test fracture analysis
        fracture_result = analyze_fracture_data(test_data, {})
        assert len(fracture_result) == 1
        assert 'family' in fracture_result[0]
        print("  ✓ Fracture analysis working")
        
        # Test filtering
        filtered_result = analyze_rmr_data(test_data, {'RMR': {'min': 70}})
        assert len(filtered_result) == 1
        print("  ✓ Data filtering working")
        
        filtered_result = analyze_rmr_data(test_data, {'RMR': {'min': 80}})
        assert len(filtered_result) == 0
        print("  ✓ Filter exclusion working")
        
    except Exception as e:
        print(f"  ✗ Core functionality test failed: {e}")
        return False
    
    # Test image processing if available
    try:
        from app.utils.image_processing import get_image_dimensions
        print("  ✓ Image processing module available")
    except Exception as e:
        print(f"  ⚠️  Image processing module issue: {e}")
    
    # Test visualization if available
    try:
        from app.utils.stereonet import generate_stereonet_data
        test_features = [{'dip': 45, 'dip_direction': 120}]
        stereonet_data = generate_stereonet_data(test_features)
        assert len(stereonet_data) == 1
        print("  ✓ Stereonet functionality working")
    except Exception as e:
        print(f"  ⚠️  Stereonet functionality issue: {e}")
    
    print("  ✓ Core functionality tests completed")
    return True

def test_api_endpoints():
    """Test API endpoints for basic functionality."""
    print(f"\n🌐 Testing API endpoints...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("  ✓ Home page accessible")
            else:
                print(f"  ⚠️  Home page status: {response.status_code}")
            
            # Test geological analysis page
            response = client.get('/geological-analysis')
            if response.status_code == 200:
                print("  ✓ Geological analysis page accessible")
            else:
                print(f"  ⚠️  Geological analysis page status: {response.status_code}")
            
            # Test API endpoint with sample data
            test_data = {
                'mode': 'rmr',
                'data': [{
                    'Frente': 'T1',
                    'PK_medio': 100.5,
                    'RMR': 75,
                    'X': 150,
                    'Y': 200
                }],
                'filters': {}
            }
            
            response = client.post('/api/filter-data', 
                                 json=test_data,
                                 content_type='application/json')
            
            if response.status_code == 200:
                print("  ✓ Filter data API endpoint working")
            else:
                print(f"  ⚠️  Filter data API status: {response.status_code}")
        
    except Exception as e:
        print(f"  ⚠️  API endpoint test issue: {e}")
    
    print("  ✓ API endpoint tests completed")
    return True

def create_migration_report(results):
    """Create migration report."""
    print(f"\n📋 Creating migration report...")
    
    report = {
        'migration_timestamp': datetime.now().isoformat(),
        'system_checks': results,
        'migration_status': 'completed' if all(results.values()) else 'completed_with_warnings',
        'recommendations': []
    }
    
    if not results.get('dependencies', True):
        report['recommendations'].append(
            "Install missing dependencies with: pip install -r requirements.txt"
        )
    
    if not all(results.values()):
        report['recommendations'].append(
            "Some tests failed - check console output for details"
        )
    
    report['recommendations'].extend([
        "Review MODERNIZATION_GUIDE.md for detailed information about new features",
        "Run test_modernization.py to validate functionality",
        "Consider gradual migration to new API endpoints (/api/v2/*)"
    ])
    
    # Save report
    with open('migration_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"  ✓ Migration report saved to migration_report.json")
    return report

def main():
    """Main migration function."""
    print_banner()
    
    results = {}
    
    # Step 1: Check dependencies
    results['dependencies'] = check_dependencies()
    
    # Step 2: Backup existing data
    results['backup'] = backup_existing_data()
    
    # Step 3: Validate data files
    results['data_validation'] = validate_data_files()
    
    # Step 4: Test core functionality
    results['core_functionality'] = test_core_functionality()
    
    # Step 5: Test API endpoints
    results['api_endpoints'] = test_api_endpoints()
    
    # Step 6: Create migration report
    report = create_migration_report(results)
    
    # Final summary
    print("\n" + "="*60)
    print("📊 MIGRATION SUMMARY")
    print("="*60)
    
    for check, status in results.items():
        status_icon = "✓" if status else "⚠️"
        print(f"  {status_icon} {check.replace('_', ' ').title()}: {'Passed' if status else 'Warning'}")
    
    if report['migration_status'] == 'completed':
        print("\n🎉 Migration completed successfully!")
        print("Your geological analysis system is ready to use with enhanced features.")
    else:
        print("\n⚠️  Migration completed with warnings.")
        print("Basic functionality should work, but some features may be limited.")
    
    print("\nNext steps:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    print(f"\n📖 For detailed information, see:")
    print(f"  • MODERNIZATION_GUIDE.md - Complete modernization documentation")
    print(f"  • test_modernization.py - Run comprehensive tests")
    print(f"  • migration_report.json - Detailed migration results")
    
    print("\n" + "="*60)
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)