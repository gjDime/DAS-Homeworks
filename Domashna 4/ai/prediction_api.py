from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error

app = FastAPI()


# Define a model for historical data items
class HistoricalDataItem(BaseModel):
    date: str  # Expect date as 'YYYY-MM-DD'
    average_price: float


# Define a model for the list of historical data
class HistoricalData(BaseModel):
    data: List[HistoricalDataItem]


def preprocess_data(historical_data: pd.DataFrame, window_size: int = 60):
    # Set the date as the index
    historical_data['date'] = pd.to_datetime(historical_data['date'])
    historical_data.set_index('date', inplace=True)
    historical_data = historical_data.sort_index()
    lag = 3
    periods = range(lag, 0, -1)
    historical_data = pd.concat([historical_data, historical_data.shift(periods=periods)], axis=1)
    historical_data.dropna(axis=0, inplace=True)
    # print(historical_data.head())

    X, y = historical_data.drop(columns=["average_price"]), historical_data["average_price"]
    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.3, shuffle=False)

    scaler = MinMaxScaler()
    train_X = scaler.fit_transform(train_X)
    test_X = scaler.transform(test_X)

    scaler1 = MinMaxScaler()
    train_y = scaler1.fit_transform(train_y.to_numpy().reshape(-1, 1))

    train_X = train_X.reshape(train_X.shape[0], lag, (train_X.shape[1] // lag))
    test_X = test_X.reshape(test_X.shape[0], lag, (test_X.shape[1] // lag))

    return train_X, test_X, train_y, test_y, scaler1


def create_lstm_model(input_shape):
    # Create an LSTM model
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(units=55))
    model.add(Dense(units=1, activation="sigmoid"))  # Output layer with a single neuron

    model.compile(optimizer=Adam(), loss='mean_squared_error')
    return model

def predict_next_month(historical_data: pd.DataFrame) -> float:
    # Preprocess the data
    X_train, X_val, y_train, y_val, scaler = preprocess_data(historical_data)

    # Create and train the LSTM model
    model = create_lstm_model((X_train.shape[1], 1))
    model.fit(X_train, y_train, epochs=20, batch_size=16, validation_split=0.3, verbose=1)

    # Make predictions for the next month (30 days)
    pred_y = model.predict(X_val)

    # Inverse transform the predictions to get the actual price scale
    pred_y = scaler.inverse_transform(pred_y)

    print(f'Root Mean Squared Error (RMSE): {root_mean_squared_error(y_val, pred_y)}')
    print(f'r2 score: {r2_score(y_val, pred_y)}')

    # Return the mean forecast price for the next month
    return pred_y.mean()

# Define an endpoint for predicting the stock price
@app.post("/predict-next-month/")
async def predict_next_month_price_endpoint(historical_data: HistoricalData):

    try:
        data = pd.DataFrame([item.dict() for item in historical_data.data])
        predicted_price = predict_next_month(data)
        return {"predicted_next_month_price": float(predicted_price)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app with Uvicorn (Python ASGI server)
# Command to run: uvicorn prediction_api:app --reload
