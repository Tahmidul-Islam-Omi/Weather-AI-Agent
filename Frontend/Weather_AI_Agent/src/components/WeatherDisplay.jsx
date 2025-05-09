import { Box, Typography, Chip } from '@mui/material';
import ThermostatIcon from '@mui/icons-material/Thermostat';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import AirIcon from '@mui/icons-material/Air';

function WeatherDisplay({ data }) {
    // Check if data is a string (sometimes the API returns just text)
    if (typeof data === 'string' || !data || Object.keys(data).length === 0) {
        return null;
    }

    // Extract weather data if available
    const temp = data.main?.temp;
    const humidity = data.main?.humidity;
    const windSpeed = data.wind?.speed;
    const weatherDesc = data.weather?.[0]?.description;
    const cityName = data.name;

    // If no meaningful data, don't display anything
    if (!temp && !cityName) {
        return null;
    }

    return (
        <Box
            sx={{
                mt: 2,
                p: 2,
                borderRadius: 2,
                backgroundColor: 'rgba(25, 118, 210, 0.05)',
                border: '1px dashed rgba(25, 118, 210, 0.3)'
            }}
        >
            {cityName && (
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                    {cityName}
                </Typography>
            )}

            {weatherDesc && (
                <Typography variant="body2" sx={{ mb: 2, fontStyle: 'italic' }}>
                    {weatherDesc}
                </Typography>
            )}

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {temp && (
                    <Chip
                        icon={<ThermostatIcon />}
                        label={`${Math.round(temp)}°C`}
                        size="small"
                        color="primary"
                        variant="outlined"
                    />
                )}

                {humidity && (
                    <Chip
                        icon={<WaterDropIcon />}
                        label={`Humidity: ${humidity}%`}
                        size="small"
                        color="info"
                        variant="outlined"
                    />
                )}

                {windSpeed && (
                    <Chip
                        icon={<AirIcon />}
                        label={`Wind: ${windSpeed} m/s`}
                        size="small"
                        color="default"
                        variant="outlined"
                    />
                )}
            </Box>
        </Box>
    );
}

export default WeatherDisplay;