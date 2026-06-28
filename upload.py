from huggingface_hub import HfApi
api = HfApi()

# Broadcast your local directory straight to your public Space vault
api.upload_folder(
    folder_path=".",
    repo_id="Pushkarini/cognitive-rag-backend",
    repo_type="space",
    ignore_patterns=["venv/*", "storage_vault/*", ".*"]
)
print("🚀 Master configuration files uploaded to cloud space successfully!")
