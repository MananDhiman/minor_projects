from pyspark.sql.types import DoubleType, IntegerType
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession \
.builder \
.appName("load-csv") \
.master("local[*]") \
.getOrCreate()

def read_file(file_name: str):

    df = spark.read.option("header", True).csv(f"../data/{file_name}.csv")

    df = df.na.drop()

    # Split on '-'
    parts = F.split(df["Height"], "-")

    # convert to cm
    df = df.withColumn(
        "Height",
        F.round(
            ((parts.getItem(0).cast("int") * 12) + parts.getItem(1).cast("int")) * 2.54,
            2
        )
    )

    # type conversion and lowercase column name
    df = df.select(
        df["Name"].alias("name"),
        df["Team"].alias("team"),
        df["Number"].cast(DoubleType()).cast(IntegerType()).alias("number"),
        df["Position"].alias("position"),
        df["Age"].cast(DoubleType()).cast(IntegerType()).alias("age"),
        df["Height"].alias("height"),
        df["Weight"].cast(DoubleType()).alias("weight"),
        df["College"].alias("college"),
        df["Salary"].cast(DoubleType()).alias("salary"),
    )

    # convert pounds to kg
    df = df.withColumn("weight", F.round((F.col("weight") / 2.2), 2))

    return df

# get df from file
df = read_file("nba")

df.sort( df['height'] ).show()

df.groupBy("team").avg().show()

# root
#  |-- Name: string (nullable = true)
#  |-- Team: string (nullable = true)
#  |-- Number: double (nullable = true)
#  |-- Position: string (nullable = true)
#  |-- Age: double (nullable = true)
#  |-- Height: string (nullable = true)
#  |-- Weight: double (nullable = true)
#  |-- College: string (nullable = true)
#  |-- Salary: double (nullable = true)
