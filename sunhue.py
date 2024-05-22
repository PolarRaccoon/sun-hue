import ephem
from datetime import datetime, timedelta
import pytz
import math

def get_sun_position(date_time, latitude, longitude):
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.long = str(longitude)
    obs.date = date_time
    sun = ephem.Sun(obs)
    sun.compute(obs)
    return sun.alt, sun.az

def get_sunrise_sunset(date_time, latitude, longitude):
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.long = str(longitude)
    obs.date = date_time.date()  # Use the current date for calculation
    sun = ephem.Sun(obs)
    sunrise_utc = obs.next_rising(sun).datetime()
    sunset_utc = obs.next_setting(sun).datetime()

    # Convert sunrise and sunset times to local time
    local_timezone = pytz.timezone("Europe/Berlin")
    sunrise_local = sunrise_utc.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    sunset_local = sunset_utc.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    return sunrise_local, sunset_local

def get_noon(date_time, latitude, longitude):
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.long = str(longitude)
    obs.date = date_time.date()  # Use the current date for calculation
    sun = ephem.Sun(obs)
    noon_utc = obs.next_transit(sun).datetime()
    noon_local = noon_utc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Europe/Berlin"))
    return noon_local

def classify_time(date_time, sunrise, sunset, noon):
    if date_time < sunrise:
        return "Night"
    elif date_time < sunrise + timedelta(minutes=30):
        return "Sunrise"
    elif date_time < noon:
        return "Before Noon"
    elif date_time < sunset - timedelta(minutes=30):
        return "Afternoon"
    elif date_time < sunset:
        return "Sunset"
    else:
        return "Night"

def calculate_daylight_percent(date_time, sunrise, sunset):
    daylight_duration = sunset - sunrise
    elapsed_time = date_time - sunrise
    if elapsed_time.total_seconds() < 0:
        return 0  # Before sunrise, daylight percentage is 0
    elif elapsed_time.total_seconds() > daylight_duration.total_seconds():
        return 100  # After sunset, daylight percentage is 100
    else:
        daylight_percent = (elapsed_time.total_seconds() / daylight_duration.total_seconds()) * 100
        return daylight_percent

def calculate_sun_temperature(daylight_percent):
    if daylight_percent <= 50:
        # Morning: Linear interpolation from 2000K to 5500K
        return int(2000 + (daylight_percent / 50) * (5500 - 2000))
    else:
        # Afternoon: Linear interpolation from 5500K to 2000K
        return int(5500 - ((daylight_percent - 50) / 50) * (5500 - 2000))

def kelvin_to_rgb(kelvin):
    """Converts color temperature in Kelvin to RGB values."""
    temperature = kelvin / 100.0
    
    # Red
    if temperature <= 66:
        red = 255
    else:
        red = temperature - 60
        red = 329.698727446 * (red ** -0.1332047592)
        red = min(max(red, 0), 255)
    
    # Green
    if temperature <= 66:
        green = 99.4708025861 * math.log(temperature) - 161.1195681661
    else:
        green = 288.1221695283 * ((temperature - 60) ** -0.0755148492)
    green = min(max(green, 0), 255)
    
    # Blue
    if temperature >= 66:
        blue = 255
    elif temperature <= 19:
        blue = 0
    else:
        blue = 138.5177312231 * math.log(temperature - 10) - 305.0447927307
        blue = min(max(blue, 0), 255)
    
    return int(red), int(green), int(blue)

def rgb_to_hex(rgb):
    """Converts RGB values to hexadecimal color code."""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def main():
    # Get current UTC time
    date_time_utc = datetime.utcnow()

    # Convert UTC time to local time (Weimar, Germany)
    local_timezone = pytz.timezone("Europe/Berlin")
    date_time_local = date_time_utc.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    # Get current latitude and longitude (Weimar, Germany)
    latitude = 50.9795  # Latitude of Weimar, Germany
    longitude = 11.3235  # Longitude of Weimar, Germany
    
    # Calculate sun position
    altitude, azimuth = get_sun_position(date_time_utc, latitude, longitude)
    
    # Get sunrise, sunset, and noon times
    sunrise, sunset = get_sunrise_sunset(date_time_utc, latitude, longitude)
    noon = get_noon(date_time_utc, latitude, longitude)
    
    # Classify time
    time_category = classify_time(date_time_local, sunrise, sunset, noon)

    # Calculate daylight percentage
    daylight_percent = calculate_daylight_percent(date_time_local, sunrise, sunset)
    
    # Round daylight percentage
    rounded_daylight_percent = round(daylight_percent)

    # Calculate sun color temperature
    sun_temperature = calculate_sun_temperature(rounded_daylight_percent)
    
    # Convert sun color temperature to RGB
    sun_rgb = kelvin_to_rgb(sun_temperature)
    
    # Convert RGB to hexadecimal color code
    sun_hex_color = rgb_to_hex(sun_rgb)
    
    # Output results
    print("Current local time (Weimar, Germany):", date_time_local.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
    print("Sunrise time (local time):", sunrise.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
    print("Sunset time (local time):", sunset.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
    print("Noon time (local time):", noon.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
    print("Current location (latitude, longitude):", latitude, longitude)
    print("Sun position (altitude, azimuth):", math.degrees(altitude), math.degrees(azimuth))
    print("Time category:", time_category)
    print("Daylight percentage:", rounded_daylight_percent)
    print("Sun color temperature:", sun_temperature, "Kelvin")
    print("Sun hexadecimal color code:", sun_hex_color)

if __name__ == "__main__":
    main()
