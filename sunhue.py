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

def get_moon_position(date_time, latitude, longitude):
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.long = str(longitude)
    obs.date = date_time
    moon = ephem.Moon(obs)
    moon.compute(obs)
    return moon.alt, moon.az

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

def get_midnight(date_time, latitude, longitude):
    # Approximate midnight as the midpoint between sunset and the next sunrise
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.long = str(longitude)
    obs.date = date_time.date()  # Use the current date for calculation
    sun = ephem.Sun(obs)
    sunset_utc = obs.next_setting(sun).datetime()
    obs.date = sunset_utc
    next_sunrise_utc = obs.next_rising(sun).datetime()

    midnight_utc = sunset_utc + (next_sunrise_utc - sunset_utc) / 2
    midnight_local = midnight_utc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Europe/Berlin"))
    return midnight_local

def classify_time(date_time, sunrise, noon, sunset, midnight):
    if date_time < sunrise:
        if date_time < midnight - timedelta(hours=3):
            return "Night"
        elif date_time < midnight - timedelta(hours=1):
            return "Late Night"
        else:
            return "Early Morning"
    elif date_time < sunrise + timedelta(minutes=30):
        return "Sunrise"
    elif date_time < noon:
        return "Before Noon"
    elif date_time < sunset - timedelta(minutes=30):
        return "Afternoon"
    elif date_time < sunset:
        return "Sunset"
    elif date_time < midnight - timedelta(hours=3):
        return "Evening"
    elif date_time < midnight:
        return "Dusk"
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

def calculate_night_percent(date_time, sunset, next_sunrise):
    night_duration = next_sunrise - sunset
    elapsed_time = date_time - sunset
    if elapsed_time.total_seconds() < 0:
        return 0  # Before sunset, night percentage is 0
    elif elapsed_time.total_seconds() > night_duration.total_seconds():
        return 100  # After next sunrise, night percentage is 100
    else:
        night_percent = (elapsed_time.total_seconds() / night_duration.total_seconds()) * 100
        return night_percent

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

def get_moon_phase(date_time):
    moon = ephem.Moon()
    moon.compute(date_time)
    phase = moon.phase
    return phase

def calculate_moon_color(phase):
    # Grayscale interpolation: new moon (0%) is black, full moon (100%) is white
    brightness = int((phase / 100) * 255)
    return brightness, brightness, brightness

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
    
    # Calculate midnight
    midnight = get_midnight(date_time_utc, latitude, longitude)
    
    # Calculate next sunrise (for night percentage calculation)
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.long = str(longitude)
    obs.date = sunset  # Start from the sunset time
    next_sunrise_utc = obs.next_rising(ephem.Sun()).datetime()
    next_sunrise_local = next_sunrise_utc.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    # Classify time
    time_category = classify_time(date_time_local, sunrise, noon, sunset, midnight)

    if time_category in ["Night", "Dusk", "Evening", "Early Morning", "Late Night"]:
        # Calculate moon position and phase
        moon_altitude, moon_azimuth = get_moon_position(date_time_utc, latitude, longitude)
        moon_phase = get_moon_phase(date_time_utc)
        
        # Calculate night percentage
        night_percent = calculate_night_percent(date_time_local, sunset, next_sunrise_local)
        
        # Calculate moon color based on phase
        moon_rgb = calculate_moon_color(moon_phase)
        moon_hex_color = rgb_to_hex(moon_rgb)
        
        # Output results for night
        print("Current local time (Weimar, Germany):", date_time_local.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        print("Sunrise time (local time):", sunrise.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        print("Sunset time (local time):", sunset.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        print("Noon time (local time):", noon.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        print("Midnight (local time):", midnight.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        print("Current location (latitude, longitude):", latitude, longitude)
        print("Moon position (altitude, azimuth):", math.degrees(moon_altitude), math.degrees(moon_azimuth))
        print("Moon phase (percentage):", moon_phase)
        print("Time category:", time_category)
        print("Night percentage:", round(night_percent, 2))
        print("Moon RGB color:", moon_rgb)
        print("Moon hexadecimal color code:", moon_hex_color)
    else:
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
        
        # Output results for daytime
        print("Current local time (Weimar, Germany):", date_time_local.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        print("Sunrise time (local time):", sunrise.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        print("Sunset time (local time):", sunset.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        print("Noon time (local time):", noon.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
        print("Current location (latitude, longitude):", latitude, longitude)
        print("Sun position (altitude, azimuth):", math.degrees(altitude), math.degrees(azimuth))
        print("Time category:", time_category)
        print("Daylight percentage:", rounded_daylight_percent)
        print("Sun color temperature:", sun_temperature, "Kelvin")
        print("Sun RGB color:", sun_rgb)
        print("Sun hexadecimal color code:", sun_hex_color)

if __name__ == "__main__":
    main()
