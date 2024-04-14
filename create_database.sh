# Define the database URI
DATABASE_URI="postgresql+asyncpg://*******:**************:5432/bot_database"

# Parse the URI to extract username, password and database name
DB_USER=$(echo $DATABASE_URI | grep -oP 'pgsql_user(?=:)')
DB_PASSWORD=$(echo $DATABASE_URI | grep -oP ':\K[^@]*')
DB_NAME=$(echo $DATABASE_URI | grep -oP '@[^:]*:\d*/\K.*')

# Install PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Install psycopg2-binary and asyncpg with pip, assuming you have Python and pip already installed
pip install psycopg2-binary asyncpg

# Create the user and database
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

echo "Environment setup complete."
