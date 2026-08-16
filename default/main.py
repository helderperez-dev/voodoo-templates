import uvicorn
from voodoo import create_app, config

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=config.host, 
        port=config.port, 
        reload=True, 
        ws_max_size=16777216, 
        ws_max_queue=32,
        http="h11",
        ws="auto",
        h11_max_incomplete_event_size=5242880
    )
