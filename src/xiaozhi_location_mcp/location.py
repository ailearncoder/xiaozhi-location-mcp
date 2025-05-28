from mcp.server.fastmcp import FastMCP
import logging
from xiaozhi_app.plugins import AndroidDevice
from typing import Annotated
from pydantic import Field
from enum import Enum

# Create an MCP server
mcp = FastMCP("BaiduMapsHelper")


class Provider(Enum):
    GPS = "gps"
    NETWORK = "network"
    FUSED = "fused"


def init_log():
    logger_name = "location"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # log_file_path = 'baidu_maps_mcp.log'
    # file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    # file_handler.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    # logger.propagate = False
    return logger


logger = init_log()


@mcp.tool()
def get_current_device_location(
    provider: Annotated[
        Provider,
        Field(
            description="The name of the location provider to use, should be one of ['gps', 'network', 'fused'], default is 'fused'"
        ),
    ] = Provider.FUSED,
) -> dict:
    """
    Get the current location of the device.
    Args:
        provider: The name of the location provider to use. should be one of ['gps', 'network', 'fused'], default is 'fused'
        Returns:
            dict: A dictionary containing the latitude, longitude, altitude, accuracy.
    """
    try:
        logging.info(f"Getting location from {provider.value} provider...")
        if not provider.value in ["gps", "network", "fused"]:
            return {
                "success": False,
                "error": "Invalid location provider, should be one of ['gps', 'network', 'fused']",
            }
        device = AndroidDevice()
        current_location = device.get_current_location(provider.value, "MCP Location")
        logging.info(f"Location: {current_location}")
        return current_location
    except Exception as e:
        logger.error(f"Error getting location: {e}")
        return {"success": False, "error": f"{e}"}


async def print_tools(mcp: FastMCP):
    print(await mcp.list_tools())


def load_env():
    import os
    if not os.path.exists("/app/.env"):
       return
    with open("/app/.env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key] = value

# Start the server
def run():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )
    logger.info("Starting Location Server Version 0.1.6")
    load_env()
    mcp.run(transport="stdio")
