/**
 * Geological Analysis Interactive Canvas Application
 * Provides image visualization, scaling, measurement, and geological data overlay
 */

class GeologicalAnalysis {
    constructor() {
        this.canvas = document.getElementById('geologicalCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvasOverlay = document.getElementById('canvasOverlay');
        
        // State management
        this.state = {
            image: null,
            imageLoaded: false,
            excelData: null,
            filteredData: [],
            currentMode: 'rmr',
            scale: {
                factor: null,
                pixelDistance: null,
                realDistance: null,
                points: []
            },
            zoom: 1,
            pan: { x: 0, y: 0 },
            measurements: [],
            activeTool: null,
            currentMeasurement: null,
            mousePos: { x: 0, y: 0 },
            isDragging: false,
            lastMouse: { x: 0, y: 0 }
        };
        
        this.initializeEventListeners();
        this.setupCanvas();
    }

    initializeEventListeners() {
        // File upload handlers
        document.getElementById('imageUpload').addEventListener('change', (e) => this.handleImageUpload(e));
        document.getElementById('excelUpload').addEventListener('change', (e) => this.handleExcelUpload(e));
        document.getElementById('loadData').addEventListener('click', () => this.loadAndProcessData());

        // Mode switchers
        document.querySelectorAll('input[name="analysisMode"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.switchAnalysisMode(e.target.value));
        });

        // Filter handlers
        document.getElementById('applyFilters').addEventListener('click', () => this.applyFilters());

        // Tool handlers
        document.getElementById('scaleBtn').addEventListener('click', () => this.activateTool('scale'));
        document.getElementById('measureBtn').addEventListener('click', () => this.activateTool('measure'));
        document.getElementById('clearBtn').addEventListener('click', () => this.clearAll());

        // Canvas zoom and pan
        document.getElementById('zoomIn').addEventListener('click', () => this.zoomCanvas(1.2));
        document.getElementById('zoomOut').addEventListener('click', () => this.zoomCanvas(0.8));
        document.getElementById('resetView').addEventListener('click', () => this.resetView());

        // Canvas interactions
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.onWheel(e));
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        // Scale input
        document.getElementById('realDistance').addEventListener('input', (e) => this.updateScale());

        // Window resize
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    setupCanvas() {
        this.resizeCanvas();
        this.showInstructions();
    }

    resizeCanvas() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // Set canvas size to fill container
        this.canvas.width = rect.width - 2;
        this.canvas.height = rect.height - 2;
        
        // Redraw if image is loaded
        if (this.state.imageLoaded) {
            this.drawCanvas();
        }
    }

    showInstructions() {
        this.canvasOverlay.classList.remove('hidden');
        document.getElementById('instructionText').style.display = 'block';
        document.getElementById('loadingSpinner').style.display = 'none';
    }

    showLoading() {
        this.canvasOverlay.classList.remove('hidden');
        document.getElementById('instructionText').style.display = 'none';
        document.getElementById('loadingSpinner').style.display = 'block';
    }

    hideOverlay() {
        this.canvasOverlay.classList.add('hidden');
    }

    async handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('/upload-image', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (result.success) {
                this.state.imageFilename = result.filename;
                await this.loadImage(result.filename);
                this.updateDataStatus('Imagen cargada');
            } else {
                this.showError('Error al cargar imagen: ' + result.error);
            }
        } catch (error) {
            this.showError('Error de conexión al cargar imagen');
        }
    }

    async handleExcelUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('excel', file);

        try {
            const response = await fetch('/upload-excel', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (result.success) {
                this.state.excelFilename = result.filename;
                this.updateDataStatus('Excel cargado');
            } else {
                this.showError('Error al cargar Excel: ' + result.error);
            }
        } catch (error) {
            this.showError('Error de conexión al cargar Excel');
        }
    }

    async loadAndProcessData() {
        if (!this.state.imageFilename) {
            this.showError('Por favor, cargue una imagen primero');
            return;
        }

        if (!this.state.excelFilename) {
            this.showError('Por favor, cargue un archivo Excel primero');
            return;
        }

        this.showLoading();

        try {
            // Load Excel data
            const excelResponse = await fetch('/api/load-excel-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: this.state.excelFilename })
            });

            const excelResult = await excelResponse.json();
            if (excelResult.success) {
                this.state.excelData = excelResult.data;
                this.populateFilters(excelResult.data);
                this.applyFilters();
                this.updateDataStatus('Datos procesados');
            } else {
                throw new Error(excelResult.error);
            }

        } catch (error) {
            this.showError('Error al procesar datos: ' + error.message);
        }

        this.hideOverlay();
    }

    async loadImage(filename) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                this.state.image = img;
                this.state.imageLoaded = true;
                this.resetView();
                this.drawCanvas();
                resolve();
            };
            img.onerror = reject;
            img.src = `/serve-image/${filename}`;
        });
    }

    populateFilters(data) {
        // Populate frente filter
        const frenteValues = [...new Set(data.map(d => d.Frente).filter(Boolean))];
        const frenteSelect = document.getElementById('frenteFilter');
        frenteSelect.innerHTML = '<option value="">Todos</option>';
        frenteValues.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            frenteSelect.appendChild(option);
        });

        // Populate familia filter for fractures
        const familiaValues = [...new Set(data.map(d => d.Familia).filter(Boolean))];
        const familiaSelect = document.getElementById('familiaFilter');
        familiaSelect.innerHTML = '<option value="">Todas</option>';
        familiaValues.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            familiaSelect.appendChild(option);
        });

        // Set PK range defaults
        const pkValues = data.map(d => d.PK_medio).filter(v => v != null);
        if (pkValues.length > 0) {
            document.getElementById('pkMedioMin').placeholder = Math.min(...pkValues).toFixed(2);
            document.getElementById('pkMedioMax').placeholder = Math.max(...pkValues).toFixed(2);
        }
    }

    async applyFilters() {
        if (!this.state.excelData) return;

        const filters = this.collectFilters();

        try {
            const response = await fetch('/api/filter-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: this.state.currentMode,
                    data: this.state.excelData,
                    filters: filters
                })
            });

            const result = await response.json();
            if (result.success) {
                this.state.filteredData = result.data;
                this.drawCanvas();
                this.updateDataStatus(`${result.data.length} puntos filtrados`);
            } else {
                this.showError('Error al filtrar datos: ' + result.error);
            }
        } catch (error) {
            this.showError('Error de conexión al filtrar datos');
        }
    }

    collectFilters() {
        const filters = {};

        // Frente filter
        const frente = document.getElementById('frenteFilter').value;
        if (frente) filters.Frente = frente;

        // PK medio range
        const pkMin = parseFloat(document.getElementById('pkMedioMin').value);
        const pkMax = parseFloat(document.getElementById('pkMedioMax').value);
        if (!isNaN(pkMin) || !isNaN(pkMax)) {
            filters.PK_medio = {};
            if (!isNaN(pkMin)) filters.PK_medio.min = pkMin;
            if (!isNaN(pkMax)) filters.PK_medio.max = pkMax;
        }

        // Mode-specific filters
        if (this.state.currentMode === 'rmr') {
            const rmrMin = parseFloat(document.getElementById('rmrMin').value);
            const rmrMax = parseFloat(document.getElementById('rmrMax').value);
            if (!isNaN(rmrMin) || !isNaN(rmrMax)) {
                filters.RMR = {};
                if (!isNaN(rmrMin)) filters.RMR.min = rmrMin;
                if (!isNaN(rmrMax)) filters.RMR.max = rmrMax;
            }
        } else {
            const familia = document.getElementById('familiaFilter').value;
            if (familia) filters.Familia = familia;
        }

        return filters;
    }

    switchAnalysisMode(mode) {
        this.state.currentMode = mode;

        // Show/hide mode-specific filters
        document.getElementById('rmrFilters').style.display = mode === 'rmr' ? 'block' : 'none';
        document.getElementById('fractureFilters').style.display = mode === 'fracturas' ? 'block' : 'none';

        // Show/hide legends
        document.getElementById('rmrLegend').style.display = mode === 'rmr' ? 'block' : 'none';
        document.getElementById('fractureLegend').style.display = mode === 'fracturas' ? 'block' : 'none';

        // Re-apply filters and redraw
        this.applyFilters();
    }

    activateTool(tool) {
        // Deactivate all tools first
        document.querySelectorAll('#scaleBtn, #measureBtn').forEach(btn => {
            btn.classList.remove('active', 'btn-success');
            btn.classList.add('btn-outline-primary', 'btn-outline-warning');
        });

        this.state.activeTool = tool;

        // Activate selected tool
        const button = document.getElementById(tool + 'Btn');
        button.classList.remove('btn-outline-primary', 'btn-outline-warning');
        button.classList.add('active', 'btn-success');

        // Change cursor
        this.canvas.style.cursor = tool === 'scale' ? 'crosshair' : 'crosshair';

        // Show measurements panel for measure tool
        if (tool === 'measure') {
            document.getElementById('measurementsPanel').classList.add('show');
        }
    }

    clearAll() {
        this.state.measurements = [];
        this.state.scale.points = [];
        this.state.scale.factor = null;
        this.state.activeTool = null;
        this.canvas.style.cursor = 'default';
        
        // Clear UI
        document.getElementById('measurementsTable').innerHTML = '';
        document.getElementById('scaleDisplay').textContent = 'Escala: No definida';
        document.getElementById('realDistance').value = '';

        // Deactivate tool buttons
        document.querySelectorAll('#scaleBtn, #measureBtn').forEach(btn => {
            btn.classList.remove('active', 'btn-success');
            btn.classList.add('btn-outline-primary', 'btn-outline-warning');
        });

        this.drawCanvas();
    }

    onMouseDown(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left - this.state.pan.x) / this.state.zoom;
        const y = (event.clientY - rect.top - this.state.pan.y) / this.state.zoom;

        if (this.state.activeTool === 'scale') {
            this.handleScaleClick(x, y);
        } else if (this.state.activeTool === 'measure') {
            this.handleMeasureClick(x, y);
        } else {
            // Start panning
            this.state.isDragging = true;
            this.state.lastMouse = { x: event.clientX, y: event.clientY };
            this.canvas.style.cursor = 'grabbing';
        }
    }

    onMouseMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left - this.state.pan.x) / this.state.zoom;
        const y = (event.clientY - rect.top - this.state.pan.y) / this.state.zoom;

        this.state.mousePos = { x, y };
        this.updateMouseCoordinates(Math.round(x), Math.round(y));

        if (this.state.isDragging && !this.state.activeTool) {
            // Pan the canvas
            const deltaX = event.clientX - this.state.lastMouse.x;
            const deltaY = event.clientY - this.state.lastMouse.y;

            this.state.pan.x += deltaX;
            this.state.pan.y += deltaY;
            this.state.lastMouse = { x: event.clientX, y: event.clientY };

            this.drawCanvas();
        }

        // Draw preview for active measurements
        if (this.state.currentMeasurement) {
            this.drawCanvas();
            this.drawMeasurementPreview(this.state.currentMeasurement.start, { x, y });
        }
    }

    onMouseUp(event) {
        this.state.isDragging = false;
        this.canvas.style.cursor = this.state.activeTool ? 'crosshair' : 'default';
    }

    onWheel(event) {
        event.preventDefault();
        
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1;
        
        // Zoom towards mouse position
        const newZoom = Math.max(0.1, Math.min(10, this.state.zoom * zoomFactor));
        
        // Adjust pan to zoom towards mouse
        this.state.pan.x = mouseX - (mouseX - this.state.pan.x) * (newZoom / this.state.zoom);
        this.state.pan.y = mouseY - (mouseY - this.state.pan.y) * (newZoom / this.state.zoom);
        
        this.state.zoom = newZoom;
        this.updateZoomLevel();
        this.drawCanvas();
    }

    handleScaleClick(x, y) {
        this.state.scale.points.push({ x, y });

        if (this.state.scale.points.length === 2) {
            const p1 = this.state.scale.points[0];
            const p2 = this.state.scale.points[1];
            
            this.state.scale.pixelDistance = Math.sqrt(
                Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2)
            );

            this.updateScale();
            this.state.scale.points = []; // Reset for next scaling
        }

        this.drawCanvas();
    }

    handleMeasureClick(x, y) {
        if (!this.state.currentMeasurement) {
            // Start new measurement
            this.state.currentMeasurement = {
                id: Date.now(),
                start: { x, y }
            };
        } else {
            // Complete measurement
            const end = { x, y };
            const pixelDistance = Math.sqrt(
                Math.pow(end.x - this.state.currentMeasurement.start.x, 2) + 
                Math.pow(end.y - this.state.currentMeasurement.start.y, 2)
            );

            const measurement = {
                id: this.state.currentMeasurement.id,
                start: this.state.currentMeasurement.start,
                end: end,
                pixelDistance: pixelDistance,
                realDistance: this.state.scale.factor ? pixelDistance * this.state.scale.factor : null
            };

            this.state.measurements.push(measurement);
            this.state.currentMeasurement = null;
            this.addMeasurementToTable(measurement);
            this.drawCanvas();
        }
    }

    updateScale() {
        const realDistance = parseFloat(document.getElementById('realDistance').value);
        if (this.state.scale.pixelDistance && realDistance > 0) {
            this.state.scale.factor = realDistance / this.state.scale.pixelDistance;
            this.state.scale.realDistance = realDistance;
            
            document.getElementById('scaleDisplay').textContent = 
                `Escala: 1 px = ${this.state.scale.factor.toFixed(4)} m`;
        }
    }

    zoomCanvas(factor) {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;

        // Zoom towards center
        const newZoom = Math.max(0.1, Math.min(10, this.state.zoom * factor));
        
        this.state.pan.x = centerX - (centerX - this.state.pan.x) * (newZoom / this.state.zoom);
        this.state.pan.y = centerY - (centerY - this.state.pan.y) * (newZoom / this.state.zoom);
        
        this.state.zoom = newZoom;
        this.updateZoomLevel();
        this.drawCanvas();
    }

    resetView() {
        if (!this.state.imageLoaded) return;

        // Calculate fit-to-canvas zoom
        const imgAspect = this.state.image.width / this.state.image.height;
        const canvasAspect = this.canvas.width / this.canvas.height;

        if (imgAspect > canvasAspect) {
            this.state.zoom = this.canvas.width / this.state.image.width;
        } else {
            this.state.zoom = this.canvas.height / this.state.image.height;
        }

        // Center the image
        this.state.pan.x = (this.canvas.width - this.state.image.width * this.state.zoom) / 2;
        this.state.pan.y = (this.canvas.height - this.state.image.height * this.state.zoom) / 2;

        this.updateZoomLevel();
        this.drawCanvas();
    }

    drawCanvas() {
        if (!this.state.imageLoaded) return;

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Save context for transformations
        this.ctx.save();

        // Apply zoom and pan
        this.ctx.translate(this.state.pan.x, this.state.pan.y);
        this.ctx.scale(this.state.zoom, this.state.zoom);

        // Draw image
        this.ctx.drawImage(this.state.image, 0, 0);

        // Draw geological data points
        this.drawGeologicalData();

        // Draw scale reference points
        this.drawScalePoints();

        // Draw measurements
        this.drawMeasurements();

        this.ctx.restore();
    }

    drawGeologicalData() {
        if (!this.state.filteredData || this.state.filteredData.length === 0) return;

        this.state.filteredData.forEach(point => {
            const x = this.convertToImageX(point);
            const y = this.convertToImageY(point);

            if (x !== null && y !== null) {
                this.ctx.fillStyle = point.color || '#ff0000';
                this.ctx.strokeStyle = '#000000';
                this.ctx.lineWidth = 1 / this.state.zoom; // Consistent line width

                if (this.state.currentMode === 'rmr') {
                    // Draw circles for RMR points
                    this.ctx.beginPath();
                    this.ctx.arc(x, y, 8 / this.state.zoom, 0, 2 * Math.PI);
                    this.ctx.fill();
                    this.ctx.stroke();

                    // Add RMR value text
                    if (point.rmr_value !== undefined) {
                        this.ctx.fillStyle = '#000000';
                        this.ctx.font = `${12 / this.state.zoom}px Arial`;
                        this.ctx.textAlign = 'center';
                        this.ctx.fillText(point.rmr_value.toString(), x, y - 12 / this.state.zoom);
                    }
                } else {
                    // Draw squares for fracture points
                    const size = 8 / this.state.zoom;
                    this.ctx.fillRect(x - size/2, y - size/2, size, size);
                    this.ctx.strokeRect(x - size/2, y - size/2, size, size);
                }
            }
        });
    }

    drawScalePoints() {
        this.ctx.fillStyle = '#00ff00';
        this.ctx.strokeStyle = '#000000';
        this.ctx.lineWidth = 2 / this.state.zoom;

        this.state.scale.points.forEach(point => {
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, 6 / this.state.zoom, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.stroke();
        });

        // Draw line between scale points
        if (this.state.scale.points.length === 2) {
            this.ctx.strokeStyle = '#00ff00';
            this.ctx.lineWidth = 3 / this.state.zoom;
            this.ctx.beginPath();
            this.ctx.moveTo(this.state.scale.points[0].x, this.state.scale.points[0].y);
            this.ctx.lineTo(this.state.scale.points[1].x, this.state.scale.points[1].y);
            this.ctx.stroke();
        }
    }

    drawMeasurements() {
        this.ctx.strokeStyle = '#ff6600';
        this.ctx.lineWidth = 2 / this.state.zoom;
        this.ctx.fillStyle = '#ff6600';

        this.state.measurements.forEach(measurement => {
            // Draw measurement line
            this.ctx.beginPath();
            this.ctx.moveTo(measurement.start.x, measurement.start.y);
            this.ctx.lineTo(measurement.end.x, measurement.end.y);
            this.ctx.stroke();

            // Draw endpoints
            [measurement.start, measurement.end].forEach(point => {
                this.ctx.beginPath();
                this.ctx.arc(point.x, point.y, 4 / this.state.zoom, 0, 2 * Math.PI);
                this.ctx.fill();
            });

            // Draw distance label
            const midX = (measurement.start.x + measurement.end.x) / 2;
            const midY = (measurement.start.y + measurement.end.y) / 2;
            
            this.ctx.fillStyle = '#000000';
            this.ctx.font = `${10 / this.state.zoom}px Arial`;
            this.ctx.textAlign = 'center';
            
            const displayText = measurement.realDistance ? 
                `${measurement.realDistance.toFixed(2)} m` : 
                `${measurement.pixelDistance.toFixed(0)} px`;
            
            this.ctx.fillText(displayText, midX, midY - 5 / this.state.zoom);
        });
    }

    drawMeasurementPreview(start, end) {
        this.ctx.save();
        this.ctx.translate(this.state.pan.x, this.state.pan.y);
        this.ctx.scale(this.state.zoom, this.state.zoom);

        this.ctx.strokeStyle = '#ff6600';
        this.ctx.lineWidth = 2 / this.state.zoom;
        this.ctx.setLineDash([5 / this.state.zoom, 5 / this.state.zoom]);

        this.ctx.beginPath();
        this.ctx.moveTo(start.x, start.y);
        this.ctx.lineTo(end.x, end.y);
        this.ctx.stroke();

        this.ctx.restore();
    }

    convertToImageX(point) {
        // Convert geological coordinates to image X coordinate
        // This is a simplified conversion - implement based on your coordinate system
        if (point.image_x !== undefined) return point.image_x;
        if (point.x !== undefined) return point.x;
        if (point.X !== undefined) return point.X;
        return null;
    }

    convertToImageY(point) {
        // Convert geological coordinates to image Y coordinate
        // This is a simplified conversion - implement based on your coordinate system
        if (point.image_y !== undefined) return point.image_y;
        if (point.y !== undefined) return point.y;
        if (point.Y !== undefined) return point.Y;
        return null;
    }

    addMeasurementToTable(measurement) {
        const table = document.getElementById('measurementsTable');
        const row = table.insertRow();
        
        row.innerHTML = `
            <td>${measurement.id}</td>
            <td>(${measurement.start.x.toFixed(0)}, ${measurement.start.y.toFixed(0)})</td>
            <td>(${measurement.end.x.toFixed(0)}, ${measurement.end.y.toFixed(0)})</td>
            <td>${measurement.pixelDistance.toFixed(2)}</td>
            <td>${measurement.realDistance ? measurement.realDistance.toFixed(2) + ' m' : 'N/A'}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="geologicalApp.removeMeasurement(${measurement.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
    }

    removeMeasurement(id) {
        this.state.measurements = this.state.measurements.filter(m => m.id !== id);
        this.drawCanvas();
        
        // Remove from table
        const table = document.getElementById('measurementsTable');
        for (let row of table.rows) {
            if (row.cells[0].textContent == id) {
                row.remove();
                break;
            }
        }
    }

    updateMouseCoordinates(x, y) {
        document.getElementById('mouseCoords').textContent = `Posición: (${x}, ${y})`;
    }

    updateZoomLevel() {
        document.getElementById('zoomLevel').textContent = `Zoom: ${(this.state.zoom * 100).toFixed(0)}%`;
    }

    updateDataStatus(status) {
        document.getElementById('dataStatus').textContent = `Datos: ${status}`;
    }

    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        modal.show();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.geologicalApp = new GeologicalAnalysis();
});

// Export for global access
window.GeologicalAnalysis = GeologicalAnalysis;