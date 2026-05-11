"""Disease Surveillance PySpark Pipeline — Azure Databricks."""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import os


def get_spark():
    return SparkSession.builder.appName("DiseaseSurveillancePipeline").getOrCreate()


def compute_rolling_cases(cases_df, disease: str = "Malaria", window_weeks: int = 4):
    filtered = cases_df.filter(F.col("disease") == disease)
    w = Window.partitionBy("state").orderBy("week_start").rowsBetween(-window_weeks + 1, 0)
    return (
        filtered
        .withColumn("rolling_cases", F.sum("cases").over(w))
        .withColumn("rolling_deaths", F.sum("deaths").over(w))
        .withColumn("rolling_incidence", F.avg("incidence_per_100k").over(w))
        .withColumn(
            "alert_status",
            F.when(F.col("rolling_incidence") >= 100, "RED_ALERT")
             .when(F.col("rolling_incidence") >= 50, "WATCH")
             .otherwise("NORMAL")
        )
    )


def compute_epidemic_threshold(cases_df):
    """Flag weeks where cases exceed 2 standard deviations above mean."""
    stats = (
        cases_df
        .groupBy("state", "disease")
        .agg(F.avg("cases").alias("mean_cases"),
             F.stddev("cases").alias("std_cases"))
    )
    return cases_df.join(stats, on=["state", "disease"], how="left") \
        .withColumn("is_outbreak",
                    F.col("cases") > (F.col("mean_cases") + 2 * F.col("std_cases")))


if __name__ == "__main__":
    spark = get_spark()
    cases = spark.read.csv("data/disease_cases.csv", header=True, inferSchema=True)
    rolling = compute_rolling_cases(cases)
    rolling.show(10)
    outbreak = compute_epidemic_threshold(cases)
    outbreak.filter(F.col("is_outbreak") == True).show(10)
    spark.stop()
