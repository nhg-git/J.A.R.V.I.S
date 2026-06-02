import Home from './pages/Home.jsx'

// Scanline overlay for the CRT effect
function ScanlineOverlay() {
  return <div className="scanline-overlay" />
}

export default function App() {
  return (
    <>
      <ScanlineOverlay />
      <Home />
    </>
  )
}
