import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import CloudIcon from '@mui/icons-material/Cloud';

function Header() {
    return (
        <AppBar position="static" elevation={0} sx={{ background: 'transparent', backdropFilter: 'blur(10px)' }}>
            <Toolbar>
                <CloudIcon sx={{ mr: 2, fontSize: 32, color: '#1976d2' }} />
                <Typography variant="h5" component="h1" sx={{ fontWeight: 600, color: '#1976d2' }}>
                    Weather AI Agent
                </Typography>
                <Box sx={{ flexGrow: 1 }} />
                <Typography variant="body2" sx={{ color: '#555' }}>
                    Your Intelligent Weather Assistant
                </Typography>
            </Toolbar>
        </AppBar>
    );
}

export default Header;