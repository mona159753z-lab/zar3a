import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import MyFarm from './pages/MyFarm'
import CropHealth from './pages/CropHealth'
import Assistant from './pages/Assistant'
import CropCycles from './pages/CropCycles'
import LandAnalysis from './pages/LandAnalysis'

function Placeholder({ title }) {
  return (
    <main className="min-h-screen px-6 pt-32 text-center">
      <h1 className="text-4xl font-bold text-primary">{title}</h1>
    </main>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/my-farm" element={<MyFarm />} />
        <Route path="/crop-health" element={<CropHealth />} />
        <Route path="/land-analysis" element={<LandAnalysis />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/crop-cycles" element={<CropCycles />} />
      </Routes>
    </BrowserRouter>
  )
}