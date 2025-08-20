from app import create_app, run_hybrid_server

app = create_app()

if __name__ == "__main__":
    # Run with enhanced capabilities
    run_hybrid_server(debug=True)