#!/bin/bash

# Define directories to create
dirs=(
    "app"
    "app/models"
    "app/database"
    "app/schemas"
    "app/services"
    "app/api"
    "migrations"
    "tests"
)

# Create the directory structure
echo "Creating directories..."
for dir in "${dirs[@]}"; do
    mkdir -p $dir
    echo "Created $dir"
done

# Move existing model files
echo "Moving model files to app/models/..."
mv models.py app/models/  # Adjust this if you have multiple model files or different names

# Create __init__.py files to make directories into Python packages
echo "Creating __init__.py in each package..."
for dir in "${dirs[@]}"; do
    touch $dir/__init__.py
done

# Move other Python files into the appropriate directories
# You will need to update these commands based on your actual files
mv handlers.py app/api/
#mv services.py app/services/
# mv schemas.py app/schemas/

# Optionally, you can rename models.py to base.py or similar
# mv app/models/models.py app/models/base.py

# Create placeholder files if necessary
 touch app/main.py
 touch app/database/engine.py
 touch migrations/README.md
 touch tests/test_models.py

echo "Done restructuring the project."