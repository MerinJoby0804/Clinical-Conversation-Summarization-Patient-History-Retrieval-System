
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square, Search, User, Activity, LogOut, CheckCircle, Save, Calendar, ArrowRight, Trash2, ArrowLeft, XCircle, Settings, Hexagon } from 'lucide-react';

// --- INITIAL MOCK DATA ---
const INITIAL_HISTORY = [
  { id: 1, date: "2023-10-12", diagnosis: "Viral Fever", summary: "Patient presented with high temp..." },
  { id: 2, date: "2023-11-05", diagnosis: "General Checkup", summary: "Routine vitals normal..." },
];

const MOCK_SOAP = {
  subjective: "Patient reports mild chest pain and shortness of breath.",
  objective: "BP 120/80, Pulse 98. Lungs clear.",
  assessment: "Possible mild angina or anxiety-induced stress.",
  plan: "ECG recommended. Prescribed rest and hydration."
};

// --- HOOKS ---
const useParallax = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const handleMouseMove = (e) => {
    const x = (e.clientX / window.innerWidth) * 2 - 1;
    const y = (e.clientY / window.innerHeight) * 2 - 1;
    setMousePosition({ x, y });
  };
  return { mousePosition, handleMouseMove };
};

// --- COMPONENTS ---

// 1. GHOST SHINE TITLE COMPONENT
const GhostTitle = ({ text, size = "text-9xl" }) => (
  <div className="relative overflow-hidden p-2">
    {/* Base Text */}
    <h1 className={`${size} font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-900 via-cyan-400 to-cyan-900 tracking-tighter drop-shadow-2xl`}>
      {text}
    </h1>
    
    {/* Ghost Shine Layer */}
    <motion.div 
      className="absolute inset-0 z-10 bg-gradient-to-r from-transparent via-white/50 to-transparent w-full h-full"
      style={{ mixBlendMode: 'overlay' }}
      animate={{ x: ['-100%', '200%'] }}
      transition={{ repeat: Infinity, duration: 3, ease: "linear" }}
    />
  </div>
);

// 2. AUDIO WAVEFORM
const AudioWaveform = () => (
  <div className="flex items-center justify-center gap-1 h-16">
    {[...Array(10)].map((_, i) => (
      <motion.div
        key={i}
        className="w-2 rounded-full bg-gradient-to-t from-cyan-400 to-blue-600"
        animate={{
          height: [10, Math.random() * 50 + 20, 10],
          backgroundColor: ["#22d3ee", "#2563eb", "#22d3ee"]
        }}
        transition={{ duration: 0.5, repeat: Infinity, ease: "easeInOut", delay: i * 0.1 }}
        style={{ boxShadow: "0 0 15px #22d3ee" }}
      />
    ))}
  </div>
);

// 3. PROFESSIONAL GEOMETRIC BACKGROUND (Wheels & Hexagons)
const CyberBackground = ({ mousePosition }) => (
  <div className="fixed inset-0 z-0 bg-[#030305] overflow-hidden pointer-events-none">
    
    {/* Rotating Gear 1 (Top Left) */}
    <motion.div 
      className="absolute -top-20 -left-20 text-cyan-900/10"
      animate={{ rotate: 360 }}
      transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
      style={{ x: mousePosition.x * -20, y: mousePosition.y * -20 }}
    >
      <Settings size={600} strokeWidth={0.5} />
    </motion.div>

    {/* Rotating Gear 2 (Bottom Right) */}
    <motion.div 
      className="absolute -bottom-40 -right-40 text-blue-900/10"
      animate={{ rotate: -360 }}
      transition={{ duration: 80, repeat: Infinity, ease: "linear" }}
      style={{ x: mousePosition.x * -30, y: mousePosition.y * -30 }}
    >
      <Settings size={700} strokeWidth={0.5} />
    </motion.div>

    {/* Floating Hexagons (Professional Tech Feel) */}
    <motion.div 
      className="absolute top-1/3 right-1/4 text-emerald-900/10"
      animate={{ y: [0, -20, 0], rotate: [0, 10, 0] }}
      transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
    >
      <Hexagon size={300} strokeWidth={1} />
    </motion.div>

    {/* Grid Overlay */}
    <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_100%)]" />
    
    {/* Deep Vignette */}
    <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#000000_100%)] opacity-70" />
  </div>
);

// 4. GLASS CARD
const GlassCard = ({ children, className = "", hover = false, onClick }) => (
  <motion.div
    whileHover={hover ? { scale: 1.02, translateY: -5, boxShadow: "0 20px 40px rgba(6,182,212,0.15)" } : {}}
    whileTap={hover ? { scale: 0.98 } : {}}
    onClick={onClick}
    className={`backdrop-blur-xl bg-gradient-to-br from-white/10 to-transparent border border-white/10 shadow-2xl rounded-2xl p-8 relative overflow-hidden group ${className}`}
  >
    <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/5 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 pointer-events-none z-0" />
    <div className="relative z-10">{children}</div>
  </motion.div>
);

// 5. LANDING PAGE
const LandingPage = ({ onEnter }) => {
  const { mousePosition, handleMouseMove } = useParallax();
  return (
    <div className="h-screen w-full relative overflow-hidden" onMouseMove={handleMouseMove}>
      <CyberBackground mousePosition={mousePosition} />
      <div className="relative z-10 h-full overflow-y-scroll snap-y snap-mandatory scroll-smooth">
        
        <section className="h-screen flex flex-col items-center justify-center snap-start perspective-container">
          <motion.div
            style={{ 
              rotateX: mousePosition.y * 15, 
              rotateY: mousePosition.x * 15, 
              x: mousePosition.x * -20,
              y: mousePosition.y * -20,
              perspective: 1000
            }}
            className="text-center"
          >
            <GhostTitle text="VITAL EDGE" size="text-[120px] md:text-[180px]" />
            <motion.p className="mt-4 text-2xl text-cyan-200/50 tracking-[0.8em] uppercase font-light">
              Polyglot Medical Intelligence
            </motion.p>
          </motion.div>
          <motion.div className="absolute bottom-10 flex flex-col items-center gap-2 text-cyan-500/50 animate-bounce">
            <span className="text-xs tracking-widest uppercase font-bold">Scroll to Enter</span>
            <ArrowRight className="rotate-90" />
          </motion.div>
        </section>

        <section className="h-screen flex items-center justify-center snap-start px-10 perspective-container">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16 w-full max-w-7xl">
            <motion.div style={{ rotateX: mousePosition.y * 5, rotateY: mousePosition.x * 5, x: mousePosition.x * -10 }}>
              <GlassCard hover={true} className="h-[500px] flex flex-col items-center justify-center border-cyan-500/20 cursor-pointer bg-cyan-900/5" onClick={() => onEnter('doctor')}>
                <div className="w-40 h-40 bg-cyan-500/10 rounded-full flex items-center justify-center mb-10 shadow-[0_0_40px_rgba(34,211,238,0.2)] border border-cyan-400/20">
                  <Activity size={80} className="text-cyan-400" />
                </div>
                <h2 className="text-5xl font-bold text-white mb-2">DOCTOR</h2>
                <p className="text-cyan-200/60 font-light tracking-wide">AI Consultation Suite</p>
              </GlassCard>
            </motion.div>
            
            <motion.div style={{ rotateX: mousePosition.y * 5, rotateY: mousePosition.x * 5, x: mousePosition.x * 10 }}>
              <GlassCard hover={true} className="h-[500px] flex flex-col items-center justify-center border-emerald-500/20 cursor-pointer bg-emerald-900/5" onClick={() => onEnter('patient')}>
                <div className="w-40 h-40 bg-emerald-500/10 rounded-full flex items-center justify-center mb-10 shadow-[0_0_40px_rgba(52,211,153,0.2)] border border-emerald-400/20">
                  <User size={80} className="text-emerald-400" />
                </div>
                <h2 className="text-5xl font-bold text-white mb-2">PATIENT</h2>
                <p className="text-emerald-200/60 font-light tracking-wide">Personal Health History</p>
              </GlassCard>
            </motion.div>
          </div>
        </section>
      </div>
    </div>
  );
};

// 6. DOCTOR PORTAL
const DoctorPortal = ({ onLogout }) => {
  const { mousePosition, handleMouseMove } = useParallax();
  const [view, setView] = useState('login');
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [showSoap, setShowSoap] = useState(false);
  const [history, setHistory] = useState(INITIAL_HISTORY);
  
  // New Inputs State
  const [consultInfo, setConsultInfo] = useState({ 
    id: '', 
    name: '', 
    gender: 'Male', 
    type: 'General Checkup', 
    lang: 'English' 
  });

  const handleDelete = (id) => setHistory(history.filter(item => item.id !== id));
  const handleDeleteAll = () => { if(window.confirm("Delete ALL records?")) setHistory([]); };

  if (view === 'login') {
    return (
      <div className="h-screen w-full relative overflow-hidden flex items-center justify-center" onMouseMove={handleMouseMove}>
        <CyberBackground mousePosition={mousePosition} />
        <GlassCard className="w-[500px] border-cyan-500/30">
          <button onClick={onLogout} className="absolute top-6 left-6 text-cyan-400 hover:text-white transition flex items-center gap-2 text-xs font-bold uppercase tracking-widest"><ArrowLeft size={16} /> Back</button>
          <h2 className="text-3xl font-bold text-center mt-6 mb-8 text-white">System Login</h2>
          <form className="space-y-6">
            <input type="text" className="w-full bg-black/40 border border-white/10 rounded-lg p-4 text-white focus:border-cyan-400 transition-all outline-none" placeholder="Doctor ID" />
            <input type="password" className="w-full bg-black/40 border border-white/10 rounded-lg p-4 text-white focus:border-cyan-400 transition-all outline-none" placeholder="Password" />
            <button onClick={(e) => {e.preventDefault(); setView('dashboard')}} className="w-full bg-cyan-600 hover:bg-cyan-500 py-4 rounded-lg font-bold text-white shadow-lg transition-all">ACCESS PORTAL</button>
          </form>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="h-screen w-full relative overflow-hidden flex bg-[#030305] text-white" onMouseMove={handleMouseMove}>
      <CyberBackground mousePosition={mousePosition} />
      
      {/* Sidebar */}
      <div className="w-20 md:w-72 backdrop-blur-2xl bg-black/50 border-r border-white/5 z-20 flex flex-col justify-between p-6">
        <div>
          <div className="flex items-center gap-3 mb-12 text-cyan-400">
            <Activity size={32} />
            <span className="font-bold text-xl hidden md:block tracking-widest text-white">VITAL EDGE</span>
          </div>
          <nav className="space-y-2">
            <button onClick={() => setView('dashboard')} className={`flex items-center space-x-4 w-full p-4 rounded-lg transition-all ${view === 'dashboard' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-gray-400 hover:bg-white/5'}`}><Search size={20} /> <span className="hidden md:block text-sm font-medium">Find Patient</span></button>
            <button onClick={() => setView('consultation')} className={`flex items-center space-x-4 w-full p-4 rounded-lg transition-all ${view === 'consultation' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-gray-400 hover:bg-white/5'}`}><Mic size={20} /> <span className="hidden md:block text-sm font-medium">Consultation</span></button>
          </nav>
        </div>
        <button onClick={onLogout} className="flex items-center space-x-3 text-red-400 hover:text-red-300 p-2"><LogOut size={20} /> <span className="hidden md:block text-sm">Disconnect</span></button>
      </div>

      <div className="flex-1 z-10 p-10 overflow-y-auto">
        {view === 'dashboard' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="flex justify-between items-center mb-8">
              <h1 className="text-4xl font-bold">Patient Records</h1>
              {history.length > 0 && <button onClick={handleDeleteAll} className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-2 rounded-lg hover:bg-red-500/20 transition-all text-sm"><XCircle size={16} /> Clear DB</button>}
            </div>
            <div className="flex gap-4 mb-8">
              <input type="text" placeholder="Search ID..." className="flex-1 bg-white/5 border border-white/10 rounded-lg p-4 text-white focus:border-cyan-500 outline-none" />
              <button className="bg-cyan-600 px-8 rounded-lg font-bold">Search</button>
            </div>
            <div className="grid gap-4">
              <AnimatePresence>
                {history.map((h) => (
                  <motion.div key={h.id} exit={{ opacity: 0, x: -50 }} layout>
                    <GlassCard className="border-l-4 border-l-cyan-500 bg-white/5 p-6 flex justify-between">
                      <div><h3 className="text-xl font-bold text-cyan-100">{h.diagnosis}</h3><p className="text-gray-400 text-sm mt-1">{h.summary}</p></div>
                      <button onClick={() => handleDelete(h.id)} className="text-gray-500 hover:text-red-500"><Trash2 size={20} /></button>
                    </GlassCard>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        )}

        {view === 'consultation' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-5xl mx-auto">
            <h1 className="text-4xl font-bold mb-8 text-cyan-50">New Consultation</h1>
            {!transcript && (
              <GlassCard className="mb-8 border-cyan-500/20">
                {/* NEW INPUT FIELDS GRID */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                  <div className="space-y-2">
                    <label className="text-xs text-cyan-400 uppercase tracking-wider font-bold">Patient ID</label>
                    <input type="text" className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white focus:border-cyan-500 outline-none" placeholder="Ex: P-1024" 
                      onChange={(e) => setConsultInfo({...consultInfo, id: e.target.value})} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs text-cyan-400 uppercase tracking-wider font-bold">Patient Name</label>
                    <input type="text" className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white focus:border-cyan-500 outline-none" placeholder="Ex: John Doe"
                      onChange={(e) => setConsultInfo({...consultInfo, name: e.target.value})} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs text-cyan-400 uppercase tracking-wider font-bold">Gender</label>
                    <select className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white focus:border-cyan-500 outline-none"
                      onChange={(e) => setConsultInfo({...consultInfo, gender: e.target.value})}>
                      <option>Male</option><option>Female</option><option>Other</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs text-cyan-400 uppercase tracking-wider font-bold">Language</label>
                    <select className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white focus:border-cyan-500 outline-none">
                      <option>English</option><option>Malayalam</option><option>Hindi</option>
                    </select>
                  </div>
                </div>

                <div className="flex flex-col items-center py-8 border-t border-white/5">
                  {recording ? (
                     <div className="flex flex-col items-center gap-6 w-full">
                        <div className="w-full max-w-md h-24 flex items-center justify-center bg-black/40 rounded-xl border border-white/5">
                           <AudioWaveform />
                        </div>
                        <button onClick={() => {setRecording(false); setTranscript("Patient complains of mild chest pain...")}} className="w-20 h-20 rounded-full bg-cyan-500/20 border border-cyan-500 flex items-center justify-center animate-pulse">
                           <Square fill="currentColor" className="text-cyan-400" />
                        </button>
                        <p className="text-cyan-400 text-sm tracking-widest uppercase">Recording Active...</p>
                     </div>
                  ) : (
                    <button onClick={() => setRecording(true)} className="flex flex-col items-center gap-4 group">
                      <div className="w-24 h-24 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center group-hover:bg-red-500/20 transition-all shadow-[0_0_30px_rgba(239,68,68,0.2)]">
                        <Mic size={40} className="text-red-500" />
                      </div>
                      <span className="text-sm font-bold text-gray-400 group-hover:text-white uppercase tracking-wider">Start Recording</span>
                    </button>
                  )}
                </div>
              </GlassCard>
            )}

            {transcript && !showSoap && (
              <GlassCard className="animate-fade-in border-green-500/20">
                <h3 className="font-bold text-lg mb-4 flex items-center gap-2 text-green-400"><CheckCircle size={20}/> Transcript Ready</h3>
                <textarea className="w-full h-40 p-4 rounded-lg bg-black/40 border border-white/10 text-gray-300 font-mono text-sm focus:border-green-500 outline-none" value={transcript} onChange={(e) => setTranscript(e.target.value)} />
                <div className="mt-4 flex justify-end">
                  <button onClick={() => setShowSoap(true)} className="bg-cyan-600 px-6 py-3 rounded-lg font-bold flex items-center gap-2 hover:bg-cyan-500 transition-all">
                    <Activity size={18} /> Generate SOAP
                  </button>
                </div>
              </GlassCard>
            )}

            {showSoap && (
              <GlassCard className="mt-6 border-t-4 border-t-emerald-500 bg-emerald-900/10">
                <h2 className="text-2xl font-bold mb-6 text-emerald-400">SOAP Report</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(MOCK_SOAP).map(([key, value]) => (
                    <div key={key} className="p-5 bg-black/40 rounded-xl border border-white/5">
                      <span className="font-bold text-emerald-500 block mb-2 uppercase text-xs tracking-wider">{key}</span>
                      <p className="text-gray-300 text-sm">{value}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-8 flex justify-end gap-4">
                  <button onClick={() => {setTranscript(""); setShowSoap(false)}} className="px-4 py-2 text-gray-500 hover:text-white">Discard</button>
                  <button className="bg-emerald-600 px-6 py-3 rounded-lg font-bold flex items-center gap-2 hover:bg-emerald-500 transition-all"><Save size={18} /> Save Record</button>
                </div>
              </GlassCard>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

// 7. PATIENT PORTAL
const PatientPortal = ({ onLogout }) => {
  const { mousePosition, handleMouseMove } = useParallax();
  const [loggedIn, setLoggedIn] = useState(false);

  if (!loggedIn) {
    return (
      <div className="h-screen w-full relative overflow-hidden flex items-center justify-center" onMouseMove={handleMouseMove}>
        <CyberBackground mousePosition={mousePosition} />
        <GlassCard className="w-[450px] border-emerald-500/30">
          <button onClick={onLogout} className="absolute top-6 left-6 text-emerald-400 hover:text-white transition flex items-center gap-2 text-xs font-bold uppercase tracking-widest"><ArrowLeft size={16} /> Back</button>
          <h2 className="text-3xl font-bold text-center mt-6 mb-8 text-white">Patient Access</h2>
          <form className="space-y-6">
            <input type="text" className="w-full bg-black/40 border border-white/10 rounded-lg p-4 text-white focus:border-emerald-500 outline-none" placeholder="Patient ID" />
            <input type="date" className="w-full bg-black/40 border border-white/10 rounded-lg p-4 text-gray-400 focus:border-emerald-500 outline-none" />
            <button onClick={(e) => {e.preventDefault(); setLoggedIn(true)}} className="w-full bg-emerald-600 hover:bg-emerald-500 py-4 rounded-lg font-bold text-white shadow-lg transition-all">VIEW RECORDS</button>
          </form>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#030305] text-white relative" onMouseMove={handleMouseMove}>
      <CyberBackground mousePosition={mousePosition} />
      <header className="relative z-20 backdrop-blur-xl bg-black/50 border-b border-white/10 p-6 flex justify-between items-center sticky top-0">
        <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <h1 className="text-xl font-bold text-emerald-400 tracking-wider">VITAL EDGE PATIENT</h1>
        </div>
        <button onClick={onLogout} className="flex items-center gap-2 bg-white/5 px-4 py-2 rounded-lg hover:bg-white/10 transition border border-white/10"><LogOut size={16} /> Logout</button>
      </header>
      <main className="max-w-4xl mx-auto p-10 relative z-10">
        <GlassCard className="mb-12 border-emerald-500/20 bg-gradient-to-r from-emerald-900/20 to-transparent">
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-emerald-500/10 flex items-center justify-center text-3xl font-bold text-emerald-400 border border-emerald-500/30">JD</div>
            <div><h2 className="text-2xl font-bold text-white">John Doe</h2><p className="text-emerald-200/60">34 Years • Male • O+ Blood</p></div>
          </div>
        </GlassCard>
        <h3 className="text-xl font-bold mb-8 text-gray-300 flex items-center gap-2"><Calendar className="text-emerald-500" /> Medical Timeline</h3>
        <div className="relative border-l border-white/10 ml-6 space-y-12 pb-20">
          {INITIAL_HISTORY.map((record, index) => (
            <div key={index} className="ml-10 relative">
              <div className="absolute -left-[45px] top-6 w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_10px_#10b981]" />
              <GlassCard hover={true} className="border-l-2 border-l-emerald-500/50">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-xl font-bold text-emerald-100">{record.diagnosis}</h4>
                  <span className="text-xs bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded border border-emerald-500/20">{record.date}</span>
                </div>
                <p className="text-gray-400 leading-relaxed text-sm">{record.summary}</p>
              </GlassCard>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};

// 8. MAIN APP
const App = () => {
  const [role, setRole] = useState(null);
  return (
    <AnimatePresence mode='wait'>
      {!role && <LandingPage key="landing" onEnter={setRole} />}
      {role === 'doctor' && <DoctorPortal key="doc" onLogout={() => setRole(null)} />}
      {role === 'patient' && <PatientPortal key="pat" onLogout={() => setRole(null)} />}
    </AnimatePresence>
  );
};

export default App;



