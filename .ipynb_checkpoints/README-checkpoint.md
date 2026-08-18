# NYC Taxi Analysis

Source: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Question: How can taxi companies position drivers to maximize ride volume? 

Business Question: Where and when should taxi drivers position themselves to maximize ride opportunities and revenue?

## Data Cleaning

In the initial stages of cleaning the data, I did the following:
- Filtered out trips where the pickup was outside of the current month and where the dropoff was before the current month, leaving the trips where dropoffs occured after the month end, if the trip started in the current month
- Excldued trips where the payment type was 0 (Flex Fare), as these consistently had missing data for passenger counts and fees.
- Excluded trips over 100 miles, as trips in NYC that go over 100 miles would be considered abnormal
- Found and separated refund trips by getting the absolute value of fare amount and total amount, then finding duplicates based on pickup/dropoff times, passenger counts, trip distance, location ids, and the absolute amounts.
    - These rows were separated into their own dataframe and saved for later analysis if needed
- Excluded trips where the amount's were negative, but were not refunds
    - Separated into their own dataframe as well
- Excluded trips where the passenger count was 0
    - Separated into their own dataframe as well
- Swapped pickup and dropoff times where dropoff occurred after pickup

In doing further analysis of the dataset, more invalid trips were found, so I will be going back to the cleaning function after finding out what cleaning steps still need to be taken.

### Columns to investigate
- Trip Duration
- Fare Amount
- Total Amount

### Need to Add to Cleaning
- Trip Durations limits
- Fare Amounts limits