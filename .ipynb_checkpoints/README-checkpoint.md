# NYC Taxi Analysis

Source: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Business Question

How can taxi companies position drivers to maximize ride volume and revenue?

**Analysis Question:** Where and when should taxi drivers position themselves to maximize ride opportunities and revenue?

## Data Cleaning

In the initial stages of cleaning the data, I did the following:

- Filtered trips based on pickup and dropoff dates, keeping trips that began during the specified month even if they ended after the month ended.
- Excluded trips where the payment type was 0 (Flex Fare), as these consistently had missing data for passenger counts and fees.
- Excluded trips over 100 miles, which I determined to be an appropriate upper limit after examining the distribution of trip distances.
- Found and separated potential refund trips by getting the absolute values of fare amount and total amount, then finding duplicates based on pickup/dropoff times, passenger counts, trip distance, location IDs, and absolute amounts.
    - These rows were separated into their own dataframe and saved for potential future analysis.
- Excluded trips where the fare or total amount was negative.
    - These rows were separated into their own dataframe for potential future analysis.
- Excluded trips where the passenger count was 0.
    - These rows were separated into their own dataframe for potential future analysis.
- Swapped pickup and dropoff times where the recorded pickup time occurred after the dropoff time.

## Additional Data Quality Investigation

After the initial cleaning, I investigated several columns for additional anomalies:

- Trip Duration
- Fare Amount
- Total Amount
- Trip Distance / Zero-Distance Trips

### Cleaning Updates

Based on this investigation, I added the following rules:

- Removed trips where the trip distance was 0 but the pickup and dropoff locations were different.
    - A trip recorded as starting and ending in different locations should not have a recorded distance of 0.
- Removed trips lasting 24 hours or longer.
    - These records were considered anomalous and could significantly skew analyses involving trip duration.
- Updated the month-filtering logic to more accurately determine whether a trip belonged to the specified month.
- The above removals also helped to reduce outlier fare/total amounts tremendoulsly. some of the amounts may still seem like outliers, but they are minimal. 