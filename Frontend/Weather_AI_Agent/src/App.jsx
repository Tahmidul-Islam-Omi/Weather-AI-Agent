import {
    Box,
    Container,
    CssBaseline,
    ThemeProvider,
    createTheme
} from '@mui/material';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';

// Create a custom theme with blue and light blue colors
const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2',
            light: '#42a5f5',
            dark: '#1565c0',
        },
        secondary: {
            main: '#03a9f4',
            light: '#4fc3f7',
            dark: '#0288d1',
        },
        background: {
            default: '#f5f5f5',
        },
    },
    typography: {
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    },
    components: {
        MuiPaper: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                },
            },
        },
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Box
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    minHeight: '100vh',
                    background: 'linear-gradient(to bottom, #e1f5fe, #ffffff)'
                }}
            >
                <Header />
                <Container maxWidth="md" sx={{ flexGrow: 1, py: 4 }}>
                    <ChatInterface />
                </Container>
            </Box>
        </ThemeProvider>
    );
}

export default App;