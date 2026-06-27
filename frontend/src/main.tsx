import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import App from './App'
import { ThemeModeProvider } from './context/ThemeModeContext'
import { AnalysisProvider } from './context/AnalysisContext'
import './styles.css'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ThemeModeProvider>
      <AnalysisProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AnalysisProvider>
    </ThemeModeProvider>
  </React.StrictMode>,
)
