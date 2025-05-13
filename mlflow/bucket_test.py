import mlflow 
import os 
from dotenv import load_dotenv

load_dotenv()

os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL")

mlflow.set_tracking_uri("http://localhost:5001")
mlflow.set_experiment("buekct-test")

with mlflow.start_run():
    mlflow.log_param("param1", 5)
    mlflow.log_metric("accuracy", 0.92)
    with open("output.txt", "w") as f:
        f.write("test artifact")
    mlflow.log_artifact("output.txt")


