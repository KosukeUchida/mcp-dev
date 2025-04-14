from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# initialize the FastMCP instance
mcp = FastMCP("whather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """
    Make a request to the NWS API with proper error handling.
    Args:
        url (str): The URL to request.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
        except httpx.RequestError as e:
            print(f"Request error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    return None

def format_alert(feature: dict) -> str:
    """
    Format an alert feature into a readable string.
    Args:
        feature (dict): The feature dictionary containing alert information.
    Returns:
        str: Formatted alert information.
    """
    props = feature["properties"]
    return f"""
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc')}
        Serverity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', 'No description available')}
        Instruction: {props.get('instruction', 'No instruction available')}
    """

@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    Get weather alerts for a US state.
    Args:
        state (str): Two-letter US state code (e.g., CA, NY )
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    
    if not data["features"]:
        return "No weather alerts for this state."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Get weather forecast for a location
    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."
    
    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."
    
    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecast = []
    for period in periods[:5]: # Only show next 5 periods
        forecast = f"""
            Name: {period['name']}
            Temperature: {period['temperature']}°{period['temperatureUnit']}
            Wind: {period['windSpeed']} {period['windDirection']}
            Forecast: {period['detailedForecast']}
        """
        forecast.append(forecast)

    return "\n---\n".join(forecast)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')