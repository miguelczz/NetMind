import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ChatProvider } from './contexts/ChatContext'
import { NetworkProvider } from './contexts/NetworkContext'
import Layout from './components/layout/Layout'
import DashboardPage from './pages/DashboardPage'
import GeoTracePage from './pages/GeoTracePage'
import ChatPage from './pages/ChatPage'
import FilesPage from './pages/FilesPage'

function App() {
  return (
    <Router>
      <ChatProvider>
        <NetworkProvider>
            <Layout>
            <Routes>
                <Route path="/" element={<ChatPage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/geotrace" element={<GeoTracePage />} />
                <Route path="/files" element={<FilesPage />} />
            </Routes>
            </Layout>
        </NetworkProvider>
      </ChatProvider>
    </Router>
  )
}

export default App

