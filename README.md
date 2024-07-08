## Sustainable City Management

### Table of contents
- [Description](#description)
- [Architecture](#architecture)
- [Deployment instructions](#deployment-instructions)
- [Demonstration and presentation videos](#demonstration-and-presentation-videos)

### Description
This project implements a software system to monitor the means of public transport in Dublin and provide recommendations for their sustainable and efficient management. The supported types of public transport include buses, bikes, trams and pedestian ways.

The real-time monitoring part of the system collects data from publicly available APIs. It visualises information about most delayed bus routes, current availability of shared bikes per station, position of trams and pedestian footfall density. It also includes forecasts about bike availability in the next hours through a custom Prophet model.

Moreover, the system provides two different types of recommendations. First, a greedy algorithm proposes dynamic bike reallocation between neighbouring stations, to prevent stations from running out of bikes. Second, a genetic algorithm is used to optimise bus and tram timetables. The algorithm takes as input the target number of daily routes, and the time of the first and the last routes. The optimisation objectives are the minimisation of the passenger waiting time and the approximation of the target number of routes.

### Architecture
The software system consists of 4 distinct components:
1. A Postgres database.
2. An ETL pipeline implemented with pySpark that ingest data from the publicly available transport APIs and stores it in the database.
3. An MVC web application implemented with Django that covers backend functionalities.
4. A Streamlit frontend application.

### Deployment instructions

1. Create virtual environments and install requirements:
   ```
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
   ```

2. Run migrations
   ```
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Run ETL pre-deployment scripts
   ```
   cd etl
   python scripts.py
   ```

4. Run the ETL pipeline  
   ```spark-submit --master local[*] --jars ./Driver/postgresql-42.7.1.jar ./ingest.py```

5. Start the Django application  
   ```python manage.py runserver```

6. Start the streamlit application  
   ```streamlit run streamlit-app.py```

### Demonstration and presentation videos
You can watch a demonstration [here](https://drive.google.com/file/d/159uGx2GnFrb4HZM1Tuk_1dqRhI2NZkuw/view?usp=drive_link) and a high-level presentation of the project [here](https://drive.google.com/file/d/1SACdzHuJ0Iw6ntNmT1s3tBe_czpthQHB/view?usp=drive_link)
