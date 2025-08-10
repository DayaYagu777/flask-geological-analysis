# Geological Analysis Application

This project is a web-based application designed for geological analysis, providing tools for image analysis, data visualization, and structural geology analysis. The application is built using Flask and includes various features to facilitate geological excavation front measurements.

## Features

- **Interactive Image Analysis Tool**: Analyze geological images with various processing capabilities.
- **Data Visualization Dashboard**: Visualize data with filtering options for better insights.
- **Stereonet Plotting**: Create stereonet plots for structural geology analysis.
- **RMR Visualization**: Color-coded visualization of excavation phases based on RMR.
- **File Upload System**: Upload images and Excel data for analysis.

## Project Structure

```
geological-analysis-app
├── app
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── forms.py
│   ├── utils
│   │   ├── image_processing.py
│   │   ├── data_analysis.py
│   │   └── stereonet.py
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   ├── js
│   │   │   └── main.js
│   │   └── uploads
│   └── templates
│       ├── base.html
│       ├── dashboard.html
│       ├── upload.html
│       ├── analysis.html
│       └── login.html
├── requirements.txt
├── config.py
├── run.py
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd geological-analysis-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application settings in `config.py`.

## Usage

1. Run the application:
   ```
   python run.py
   ```

2. Access the application in your web browser at `http://127.0.0.1:5000`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.