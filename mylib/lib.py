"""
library functions
"""

import os
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col

from pyspark.sql.types import StructType, StructField, IntegerType, StringType

LOG_FILE = "pyspark_output.md"

def log_output(operation, output, query=None):
    """adds to a markdown file"""
    with open(LOG_FILE, "a") as file:
        file.write(f"The operation is {operation}\n\n")
        if query:
            file.write(f"The query is {query}\n\n")
        file.write("The truncated output is: \n\n")
        file.write(output)
        file.write("\n\n")


def start_spark(appName):
    spark = SparkSession.builder.appName(appName).getOrCreate()
    return spark


def end_spark(spark):
    spark.stop()
    return "stopped spark session"


def extract(
    url="https://raw.githubusercontent.com/lilah-duboff/data-for-URLS/refs/heads/main/table_1_remote_work_mental_health_data.csv",
    file_path="data/table_1_remote_work_mental_health_data.csv",
    directory="data",
):
    """Extract a url to a file path"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    with requests.get(url) as r:
        with open(file_path, "wb") as f:
            f.write(r.content)

    return file_path


def load_data(
    spark,
    data="data/table_1_remote_work_mental_health_data.csv",
    name="remote_health_1",
):
    """load data"""
    # data preprocessing by setting schema
    schema = StructType(
        [
            StructField("Employee_ID", StringType(), True),
            StructField("Age", IntegerType(), True),
            StructField("Gender", StringType(), True),
            StructField("Job_Role", StringType(), True),
            StructField("Industry", StringType(), True),
            StructField("Years_of_Experience", IntegerType(), True),
            StructField("Work_Location", StringType(), True),
            StructField("Hours_Worked_Per_Week", IntegerType(), True),
            StructField("Number_of_Virtual_Meetings", IntegerType(), True),
            StructField("Work_Life_Balance_Rating", IntegerType(), True),
        ]
    )

    df = spark.read.option("header", "false").schema(schema).csv(data)

    log_output("load data", df.limit(10).toPandas().to_markdown())

    return df


def query(spark, df, query, name):
    """queries using spark sql"""
    df = df.createOrReplaceTempView(name)

    log_output("query data", spark.sql(query).toPandas().to_markdown(), query)

    return spark.sql(query).show()


def describe(df):
    summary_stats_str = df.describe().toPandas().to_markdown()
    log_output("describe data", summary_stats_str)

    return df.describe().show()


def example_transform(df):
    """does an example transformation on a predefiend dataset"""
    conditions = [
        (col("Work_Location") == "Hybrid") | (col("Work_Location") == "Onsite"),
        (col("Work_Location") == "Remote"),
    ]

    categories = ["Onsite", "Remote"]

    df = df.withColumn(
        "Occupation_Category",
        when(conditions[0], categories[0])
        .when(conditions[1], categories[1])
        .otherwise("Other"),
    )

    log_output("transform data", df.limit(10).toPandas().to_markdown())

    return df.show()
