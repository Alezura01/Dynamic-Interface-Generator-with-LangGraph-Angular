from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

client = Client()
dataset_name = "Dataset preventivi"

run_ids = ['f460fac0-75c8-4701-a2fb-23e4fd89cd6f','9023161c-d5c3-4e53-b2b5-d5bbefd330ad', 'f2f4da52-bc6e-4fef-a43d-e461754a4e31', 'f1c8510f-47b2-470f-828e-d6b7150da64f', '2d0450f6-b8aa-424a-8a8b-749a8586848f', '3f8b110e-050d-464b-a376-bff5c7dca4bd', 'fff3e03d-679f-4e06-a472-db2ea4ff8be1']

runs = client.list_runs(
    project_name = "default",
    run_ids = run_ids
)

dataset = client.create_dataset(dataset_name, description="Dataset che raccoglie le tipologie di preventivi")
examples = [{"inputs": run.inputs, "outputs": run.outputs} for run in runs]

client.create_examples(
  dataset_id=dataset.id,
  examples=examples
)




