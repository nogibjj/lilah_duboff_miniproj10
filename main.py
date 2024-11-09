"""
Main cli or app entry point
"""

from mylib.lib import (
    extract,
    load_data,
    describe,
    query,
    example_transform,
    start_spark,
    end_spark,
)


def main():
    # extract data
    extract()
    # start spark session
    spark = start_spark("remote_health_1")
    # load data into dataframe
    df = load_data(spark)
    # example metrics
    describe(df)
    # query
    query(
        spark,
        df,
        """SELECT Industry, COUNT(Employee_ID)
        AS Number_Of_Employees 
        FROM remote_health_1 
        GROUP BY Industry 
        ORDER BY Number_Of_Employees DESC;""",
        "remote_health_1",
    )
    # example transform
    example_transform(df)
    # end spark session
    end_spark(spark)


if __name__ == "__main__":
    main()
