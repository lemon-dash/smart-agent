"""
SmartAgent - 天气查询工具
演示如何封装 REST API 作为 Agent 工具
"""

from __future__ import annotations

from typing import Any

import httpx

from .base import BaseTool, ToolResult


class WeatherTool(BaseTool):
    """
    天气查询工具

    使用 Open-Meteo 免费 API（无需 API Key）
    演示了：
    1. 参数验证
    2. 外部 API 调用
    3. 数据格式化输出
    """

    # 城市名到经纬度的映射（简化版）
    _CITY_COORDS = {
        "北京": (39.9042, 116.4074),
        "上海": (31.2304, 121.4737),
        "广州": (23.1291, 113.2644),
        "深圳": (22.5431, 114.0579),
        "杭州": (30.2741, 120.1551),
        "成都": (30.5728, 104.0668),
        "武汉": (30.5928, 114.3055),
        "南京": (32.0603, 118.7969),
        "西安": (34.3416, 108.9398),
        "重庆": (29.4316, 106.9123),
        "beijing": (39.9042, 116.4074),
        "shanghai": (31.2304, 121.4737),
        "tokyo": (35.6762, 139.6503),
        "new york": (40.7128, -74.0060),
        "london": (51.5074, -0.1278),
        "paris": (48.8566, 2.3522),
    }

    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return (
            "查询城市天气信息。支持中英文城市名。"
            "返回当前温度、湿度、风速、天气状况等信息。"
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如 '北京'、'上海'、'Tokyo'",
                },
            },
            "required": ["city"],
        }

    def execute(self, city: str, **kwargs: Any) -> ToolResult:
        """查询天气"""
        try:
            city_lower = city.lower().strip()

            if city_lower not in self._CITY_COORDS:
                supported = ", ".join(sorted(set(
                    k for k in self._CITY_COORDS.keys() if not k.isascii()
                )))
                return ToolResult(
                    success=False,
                    error=f"不支持的城市 '{city}'。支持的城市: {supported}",
                )

            lat, lon = self._CITY_COORDS[city_lower]

            # 调用 Open-Meteo API
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "timezone": "auto",
            }

            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            current = data.get("current", {})

            # 天气代码转中文描述
            weather_codes = {
                0: "☀️ 晴天", 1: "🌤️ 大部晴朗", 2: "⛅ 多云",
                3: "☁️ 阴天", 45: "🌫️ 雾", 48: "🌫️ 冻雾",
                51: "🌦️ 小雨", 53: "🌦️ 中雨", 55: "🌧️ 大雨",
                61: "🌧️ 小雨", 63: "🌧️ 中雨", 65: "🌧️ 大雨",
                71: "🌨️ 小雪", 73: "🌨️ 中雪", 75: "❄️ 大雪",
                80: "🌦️ 阵雨", 95: "⛈️ 雷暴",
            }

            weather_code = current.get("weather_code", 0)
            weather_desc = weather_codes.get(weather_code, "未知")

            result = (
                f"📍 {city} 天气\n"
                f"{'=' * 30}\n"
                f"🌡️ 温度: {current.get('temperature_2m', 'N/A')}°C\n"
                f"💧 湿度: {current.get('relative_humidity_2m', 'N/A')}%\n"
                f"💨 风速: {current.get('wind_speed_10m', 'N/A')} km/h\n"
                f"🌤️ 天气: {weather_desc}"
            )

            return ToolResult(success=True, data=result)

        except httpx.TimeoutException:
            return ToolResult(success=False, error="天气查询超时")
        except httpx.HTTPError as e:
            return ToolResult(success=False, error=f"天气 API 请求失败: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=f"查询出错: {str(e)}")
