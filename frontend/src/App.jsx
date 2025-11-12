import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Search from './pages/Search'
import Login from './pages/Login'
import Register from './pages/Register'
import PsychologistProfile from './pages/PsychologistProfile'
import Dashboard from './pages/Dashboard'
import PsychologistDashboard from './pages/PsychologistDashboard'
import ClientDashboard from './pages/ClientDashboard'
import AdminDashboard from './pages/AdminDashboard'
import Forum from './pages/Forum'
import EmotionDiary from './pages/EmotionDiary'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/buscar" element={<Search />} />
            <Route path="/login" element={<Login />} />
            <Route path="/cadastro" element={<Register />} />
            <Route path="/psicologo/:id" element={<PsychologistProfile />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/dashboard/psicologo" element={<PsychologistDashboard />} />
            <Route path="/dashboard/cliente" element={<ClientDashboard />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/forum" element={<Forum />} />
            <Route path="/diario" element={<EmotionDiary />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

