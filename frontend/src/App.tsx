import { BrowserRouter, Route, Routes } from 'react-router'

function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-3xl font-bold text-slate-100">Secure File Storage</h1>
      <p className="text-slate-400">Phase 1 — project setup complete.</p>
    </main>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App