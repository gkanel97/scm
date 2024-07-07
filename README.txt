Follow the next steps to set up the project:

0. Download the trained models from the following link and move them to the respective analytics folders (tram/analytics, bikes/analytics, pedestrian/analytics)
   https://drive.google.com/drive/folders/1FBYD2ISZxYxnaWcpeBOOWsg75Ds8t9go?usp=sharing

1. Create virtual environments and install requirements:
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements

   cd frontend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements

   cd etl
   python -m venv venv
   source venv/bin/actinvate
   pip install -r requirements

2. Run migrations
   cd backend
   python manage.py makemigrations
   python manage.py migrate

3. Run ETL pre-deployment scripts
   cd etl
   python scripts.py

4. Run the ETL pipeline
   spark-submit --master local[*] --jars ./Driver/postgresql-42.7.1.jar ./ingest.py

5. Start the Django application
   python manage.py runserver

6. Start the streamlit application
   streamlit run streamlit-app.py
