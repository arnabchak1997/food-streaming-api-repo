from fastapi import FastAPI, Query
import pandas as pd
import boto3
from io import StringIO
from botocore.exceptions  import NoCredentialsError, PartialCredentialsError
import uvicorn
import os


app = FastAPI()

s3_client = boto3.client( 's3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name='ap-southeast-1' )

def fetch_data(year: int = None, country: str = None, market: str = None):
    try:
        # Retrieve the object from S3
        read_file = s3_client.get_object(Bucket='food-streaming-data-bucket', Key='total_data.csv')
        # Load CSV content into a pandas DataFrame
        df = pd.read_csv(read_file['Body'],sep=',')

        print(df.shape[0])
        # Apply filters based on provided parameters
        if year is not None:
            print("1")
            df = df[df['year'] == year]
        if country is not None:
            print("2")
            df = df[df['country'] == country]
        if market is not None:
            print("3")
            df = df[df['mkt_name'] == market]

        # Fill NaN values with empty strings
        df_filter = df.fillna('')

        print(df_filter.shape[0])
        
        # Convert filtered DataFrame to JSON
        if df_filter is None or df_filter.empty:
            raise ValueError('No data found for the specified filters.')
        else:
            filtered_json = df_filter.to_json(orient='records')
            return filtered_json

    except Exception as e:
        return {'error': str(e)}

@app.get('/fetch_data')
async def fetch_data_api(year: int = Query(None), country: str = Query(None), market: str = Query(None)):
    try:
        # Call fetch_data function with provided parameters
        filtered_data = fetch_data(year, country, market)

        if filtered_data is None:
            raise ValueError('No data found for the specified filters.')
        else:
            # Return filtered data as API response
            return filtered_data
    except Exception as e:
        return {'error': str(e)}, 400

if __name__ == '__main__':
    uvicorn.run(app, port=8080, host='0.0.0.0')
