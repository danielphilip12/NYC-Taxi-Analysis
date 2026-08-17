import numpy as np
import pandas as pd
import pyarrow as pa
from pandas.tseries.offsets import MonthEnd, MonthBegin

def clean_data(df, month):
    # Standardize known column naming inconsistencies
    column_renames = {
        "Airport_fee": "airport_fee"
    }

    df = df.rename(columns=column_renames)
    month_start = pd.Timestamp(
        year=2023,
        month=month,
        day=1
    )

    month_end = month_start + MonthEnd(0)

    # Filter data to only have trips in the respective month
    df = df[(df['tpep_pickup_datetime'] >= month_start) & (df['tpep_pickup_datetime'] <= month_end) & (df['tpep_dropoff_datetime'] >= month_start)]

    # remove flex fare trips, as these contain missing data. 
    df = df[df['payment_type'] != 0]

    # Assume trips longer than 100 miles are abnormal. 
    df = df[df['trip_distance'] <= 100]

    # get absolute value for fare/total amounts for refund/duplicate checking
    df['abs_fare'] = df['fare_amount'].abs()
    df['abs_total'] = df['total_amount'].abs()

    key_columns = [
        'tpep_pickup_datetime',
        'tpep_dropoff_datetime',
        'passenger_count',
        'trip_distance',
        'PULocationID',
        'DOLocationID',
        'abs_fare',
        'abs_total'
    ]

    # for future reference. will be returned at end
    refund_candidates = df[df.duplicated(subset=key_columns, keep=False)]

    # remove duplicates from data to analyze
    df = df.drop_duplicates(subset=key_columns, keep=False)

    # for future analysis. trips with negative fares/totals
    negative_trips = df[(df['total_amount'] < 0) | (df['fare_amount'] < 0)]

    # for future reference, trips with 0 passengers
    zero_passenger = df[df['passenger_count'] <= 0]

    # remove negative trips and 0 passengers
    df = df[(df['total_amount'] >= 0) & (df['fare_amount'] >= 0) & (df['passenger_count'] > 0)]

    # Checks if pickup and dropoff times are reversed and switches them to be correct. 
    mask = df['tpep_pickup_datetime'] > df['tpep_dropoff_datetime']

    df.loc[mask, ['tpep_pickup_datetime', 'tpep_dropoff_datetime']] = (
        df.loc[mask, ['tpep_dropoff_datetime', 'tpep_pickup_datetime']].to_numpy()
    )

    return (add_columns(df), refund_candidates, negative_trips, zero_passenger)

def add_columns(df):
    df['pickup_month'] = df['tpep_pickup_datetime'].dt.month
    df['pickup_day'] = df['tpep_pickup_datetime'].dt.day
    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    df['pickup_day_of_week_num'] = df['tpep_pickup_datetime'].dt.day_of_week
    df['pickup_day_of_week'] = df['tpep_pickup_datetime'].dt.day_name()
    df['pickup_date'] = df['tpep_pickup_datetime'].dt.date
    df["is_weekend"] = (
        df["pickup_day_of_week_num"] >= 5
    )
    df['trip_duration_minutes'] = (
            df["tpep_dropoff_datetime"]
            - df["tpep_pickup_datetime"]
        ).dt.total_seconds() / 60

    return df