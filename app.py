import os
import datetime
import openai
import streamlit as st
import requests
from dotenv import load_dotenv
load_dotenv()


def W_data(city, weather_api_key):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    url = base_url + "appid=" + weather_api_key + "&q=" + city
    response = requests.get(url)
    return response.json()

def des_weather(data, openai_api_key):
    openai.api_key = openai_api_key

    try:
        temperature = data['main']['temp'] - 273.15
        description = data['weather'][0]['description']
        prompt = f"The Current Weather in your city is {description} with {temperature: .2f} Degree Celsius. Tell me what to wear in this weather and explain the weather for all general audiences."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated for the chat-based completion
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )

        return response['choices'][0]['message']['content'].strip()
    
    except Exception as e:
        return str(e)


def week_info(weather_api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}"
    response = requests.get(url)
    return response.json()

def display_week_info(data):
    try:
        st.write("=====================================================================================")
        st.title("Weekly Weather Forecast")
        displayed_dates = set()

        for day in data['list']:
            date = datetime.datetime.fromtimestamp(day['dt']).strftime('%A, %B %d')

            if date not in displayed_dates:
                displayed_dates.add(date)

                min_temp = day['main']['temp_min'] - 273.15
                max_temp = day['main']['temp_max'] - 273.15
                description = day['weather'][0]['description']

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"{date}")
                
                with col2:
                    st.write(f"{description.capitalize()}")

                with col3:
                    st.write(f"{min_temp:.2f}°C")

                with col4:
                    st.write(f"{max_temp:.2f}°C")

    except Exception as e:
        st.error("Error in displaying weekly forecast: " + str(e))


def main():
    st.sidebar.title("SmartWeather.AI")
    city = st.sidebar.text_input("Enter city name", "London")

    weather_api_key = os.getenv("weather_api_key")
    openai_api_key = os.getenv("openai_api_key")

    submit = st.sidebar.button('GetWeather')

    if submit:
        st.title("Weather Updates for " + city + ":")
        with st.spinner('Fetching weather data....'):
            weather_data = W_data(city, weather_api_key)
            print(weather_data)

        if weather_data.get("cod") != 404:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Temperature 🌡️",f"{(weather_data['main']['temp'] - 273.15):.2f}°C")
                st.metric("Humidity💧",f"{weather_data['main']['humidity']}%")

            with col2:
                st.metric("Pressure",f"{weather_data['main']['pressure']} hPa")
                st.metric("Wind Speed🍃",f"{weather_data['wind']['speed']} m/s")

            lat = weather_data['coord']['lat']
            lon = weather_data['coord']['lon']

            weather_description = des_weather(weather_data, openai_api_key)
            st.write(weather_description)


            forecast = week_info(weather_api_key, lat, lon)

            if forecast.get("cod") != "404":
                display_week_info(forecast)
            else:
                st.error("Error fetching weekly forecast data!")

if __name__ == "__main__":
    main()
