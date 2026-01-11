import traceback

try:
    import main
    print('Imported main')
    app = main.app
    app.openapi()
    print('OpenAPI generated successfully')
except Exception:
    print('Error during OpenAPI generation:')
    traceback.print_exc()
    raise
