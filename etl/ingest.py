import time
from dbutils import connectors
from pyspark.sql import SparkSession
from models import TramApiHandler, BusApiHandler, BikeApiHandler

soft_shutdown_flag = False

# A function to write the data to the database
def write_to_database(df, table_name):
    db_connector = connectors.db_connectors()
    print("Connecting")
    df.write\
    .format("jdbc")\
    .option("url", db_connector.connection_url)\
    .option("dbtable", table_name)\
    .option("driver", "org.postgresql.Driver")\
    .mode("append")\
    .save()
    print('Connected')

if __name__ == "__main__":

    interval = 300
    spark = SparkSession.builder.appName("RealTimeETL").getOrCreate()

    bus_handler = BusApiHandler.BusApiHandler()
    bike_handler = BikeApiHandler.BikeApiHandler()
    tram_handler = TramApiHandler.TramApiHandler()

    create_table_queries = []
    create_table_queries.extend(bike_handler.get_table_create_queries())
    create_table_queries.extend(tram_handler.get_table_create_queries())
    create_table_queries.extend(bus_handler.get_table_create_queries())
    pg_conn = connectors.db_connectors()
    for query in create_table_queries:
        pg_conn.pg_connect_exec(query=query)
    pg_conn.commit_transaction()
    print("Tables created successfully.")

    try:
        while not soft_shutdown_flag:
            spark_df_arr = []
            spark_df_arr.extend(bike_handler.generate_spark_dataframes(spark))
            spark_df_arr.extend(tram_handler.generate_spark_dataframes(spark))
            spark_df_arr.extend(bus_handler.generate_spark_dataframes(spark))
            for row in spark_df_arr:
                df = row.get('spark_df')
                table_name = row.get('table_name')
                write_to_database(df, table_name)
            time.sleep(interval)

    except KeyboardInterrupt:
        print("Soft shutdown initiated...")
        soft_shutdown_flag = True

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        spark.stop()
        print("Application stopped.")