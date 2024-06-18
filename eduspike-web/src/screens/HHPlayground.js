import {
    AppBar,
    Stack,
    Grid,
    Container,
    Toolbar,
    IconButton,
    Divider,
    Drawer,
    List,
    ListItem
  } from '@mui/material';
  import '../App.css';
  import HHControlPanel from '../components/HHControlPanel';
  import HHPlotting from '../components/HHPlotting';
  import PyodideWorker from '../components/PyodideWorker';
  import { createTheme } from '@mui/material/styles';
  import HomeIcon from '@mui/icons-material/Home';
  import MenuIcon from '@mui/icons-material/Menu';
  import { useNavigate } from 'react-router-dom';
  import PythonEditor from 'codehelium';
  import { useEffect, useState, useRef } from 'react';
  import { adexDefaultCodeString } from '../defaultCodeStrings';
  import { HHSimulation } from '../components/HHSimulation';

  // Following code for theme from MUI example
  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#1976d2',
      },
    },
  });
  
  export default function AdExPlayground(props) {
    const [ pyodideInstance, setPyodideInstance ] = useState();
    const [ consoleOutputs, setConsoleOutputs ] = useState([]);
    const [ editorValue, setEditorValue ] = useState(adexDefaultCodeString);
    const [ editorInitialText, setEditorInitialText ] = useState(adexDefaultCodeString);
    const [ menuOpen, setMenuOpen ] = useState(false);
  
    useEffect(() => {
      console.log("Output change");
      console.log(consoleOutputs);
    }, [consoleOutputs, setConsoleOutputs]);
  
    useEffect(() => {
      console.log("rerendering")
    }, [editorInitialText])
  
    const navigate = useNavigate();
    const returnHome = () => {
      navigate('/');
    };
  
    if(pyodideInstance == null) {
      return (
        <div className="h-[100vh] w-[100vw] content-center text-center align-cent">
          <PyodideWorker setterPyodideInstance={setPyodideInstance}/>
            <div className="flex flex-row justify-center">
              <div className="pr-1"> 
                <img 
                  src="logo-transparent-bg.png" 
                  className="w-[5vw] animate-bounce"
                  alt="logo"
                ></img>
              </div>
            </div>
        </div>
      )
    }
  
    return (
      <div className="playgroundWrapper overscroll-none overflow-y-hidden">
          <AppBar
            position="static"
            className="bg-[#010A22]"
            sx={{
              height: '6vh',
              justifyContent: 'center',
              boxShadow: 0,
              backgroundColor: '#010A22'
            }}
          >
            <Toolbar>
              <div>
              <IconButton
              size="large"
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={() => setMenuOpen(!menuOpen)}
              sx={{ mr: 1.5 }}
              >
              <MenuIcon />
              </IconButton>
              <Drawer 
                open={menuOpen} 
                onClose={() => setMenuOpen(false)}
              >
                <List>
                  <ListItem>
                    <h1 class="text-xl font-bold w-[18vw]">Hodgkin-Huxley Sandbox</h1>
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <button onClick={() => {setEditorValue(""); setMenuOpen(false)}}>
                      Exercise 1: Zero Step Current
                    </button>
                  </ListItem>
                  <ListItem>Exercise 2: Exploring Tau</ListItem>
                </List>
              </Drawer>
              </div>
              <IconButton
                edge="start"
                color="inherit"
                aria-label="menu"
                sx={{ mr: 2 }}
                onClick={returnHome}
              >
                <HomeIcon />
              </IconButton>
              <p>Hodgkin-Huxley Sandbox</p>
            </Toolbar>
          </AppBar>
        <Grid
          container
          spacing={0}
          padding={2}
          alignSelf="center"
          justifyContent="space-evenly"
        >
          <Grid item>
            <Stack spacing={2}>
              <Container
                sx={{
                  height: '42vh',
                  width: '45vw',
                  padding: '0!important'
                }}
              >
                <HHControlPanel 
                  pyodideInstance={pyodideInstance}  
                  consoleOutputSetter={setConsoleOutputs}
                />
              </Container>
              <PythonEditor 
                height="39vh" 
                width="45vw" 
                pyodideInstance={pyodideInstance} 
                consoleOutputSetter={setConsoleOutputs}
                initialValue={editorInitialText}
                editorValue={editorValue}
                editorValueSetter={setEditorValue}
              />
            </Stack>
          </Grid>
          <Grid item>
            <Stack spacing={2}>
              <Container
                sx={{
                  display: 'flex',
                  height: '42vh',
                  width: '45vw',
                  border: '1px solid #e0e0e0',
                  borderRadius: '10px',
                  alignContent: 'center',
                  justifyContent: 'center',
                }}
              >
                <HHPlotting simulationDataStr={consoleOutputs} />
              </Container>
                <HHSimulation simulationDataStr={consoleOutputs}/>
            </Stack>
          </Grid>
        </Grid>
      </div>
    );
  }
  