from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from loguru import logger
from svc.services.forecasting import Forecaster
from svc.core.config import settings
import os

router = APIRouter()

def train_model_task():
    """
    A synchronous function to be run in the background.
    """
    try:
        logger.info("Starting model training...")
        forecaster = Forecaster() # Create a new, empty forecaster
        forecaster.fit()
        logger.info("Model training completed.")

        # Ensure the directory exists
        model_dir = os.path.dirname(settings.model_path)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        logger.info(f"Saving model to {settings.model_path}...")
        forecaster.save_model(settings.model_path)
        logger.success(f"Model successfully saved to {settings.model_path}.")

    except FileNotFoundError:
        logger.error(f"Error: The directory for the model path does not exist and could not be created.")
    except IOError as e:
        logger.error(f"An I/O error occurred while saving the model: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during model training: {e}")


@router.post("/retrain-model", tags=["Admin"])
async def retrain_model(background_tasks: BackgroundTasks):
    """
    Endpoint to trigger model retraining.
    """
    logger.info("Received request to retrain model. Starting background task.")
    background_tasks.add_task(train_model_task)
    return JSONResponse(status_code=202, content={"message": "Model training started in the background."})

@router.get("/training", tags=["Admin"])
async def training_page():
    """
    Serves the admin training page.
    """
    try:
        with open("frontend/admin_training.html") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        logger.error("frontend/admin_training.html not found.")
        return HTMLResponse(content="<h1>Admin page not found</h1>", status_code=404)
