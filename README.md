import React, { useState, useEffect, useMemo, useRef } from 'react';
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInWithCustomToken, 
  signInAnonymously, 
  onAuthStateChanged 
} from 'firebase/auth';
import { 
  getFirestore, 
  collection, 
  onSnapshot, 
  addDoc, 
  doc, 
  updateDoc, 
  deleteDoc, 
  setDoc
} from 'firebase/firestore';
import { 
  Monitor, 
  Cpu, 
  Keyboard, 
  MousePointer2, 
  Printer, 
  Tv, 
  Camera, 
  HardDrive, 
  Phone, 
  Battery, 
  Wifi, 
  Radio, 
  AlertTriangle, 
  Tablet, 
  Smartphone, 
  Box, 
  Plus, 
  Search, 
  Download, 
  Settings, 
  History, 
  BarChart3, 
  LayoutDashboard, 
  FileSearch, 
  LogOut, 
  Menu, 
  X, 
  ChevronLeft, 
  CheckCircle2, 
  AlertCircle,
  FileText,
  User,
  ShieldCheck,
  Image as ImageIcon,
  Database,
  FileSignature,
  UserPlus,
  Trash2,
  PenTool,
  Grid,
  Inbox,
  Eye,
  ClipboardList,
  ArrowLeft
} from 'lucide-react';

// --- CONFIGURACIÓN DE FIREBASE ---
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';

// --- HELPER PARA RENDERIZADO SEGURO ---
const safeStr = (val) => {
  if (val === null || val === undefined) return '';
  if (typeof val === 'object') return JSON.stringify(val);
  return String(val);
};

// --- HELPER DE CHECKLIST DINÁMICO ---
const getChecklistItems = (tipo) => {
  const config = {
    'Computadores': { hw: ['Monitor', 'CPU', 'Teclado', 'Mouse'], sw: ['SO', 'Antivirus', 'Zeus'] },
    'Impresoras': { hw: ['Rodillos', 'Bandejas', 'Tóner/Cartucho', 'Conectores Físicos'], sw: ['Configuración'] },
    'Televisores': { hw: ['Pantalla', 'Control Remoto', 'Soporte', 'Puertos'], sw: ['Smart Apps', 'Firmware'] },
    'Teléfonos IP': { hw: ['Auricular', 'Pantalla', 'Teclado', 'Cables'], sw: ['Firmware', 'Registro SIP'] },
    'Planta Telefónica': { hw: ['Chasis', 'Puertos', 'Fuente Poder'], sw: ['Firmware', 'Configuración'] },
    'Switch': { hw: ['Puertos', 'Ventiladores', 'Poder'], sw: ['Firmware', 'Config VLANs'] },
    'AP': { hw: ['Antenas', 'Carcasa', 'PoE'], sw: ['Firmware', 'Controlador AP'] },
    'NVR / DVR': { hw: ['Disco Duro', 'Ventilador', 'Ptos BNC/Red'], sw: ['Firmware', 'Grabación Activa'] },
    'Cámaras de seguridad': { hw: ['Lente', 'Carcasa', 'Cableado'], sw: ['Firmware', 'Video en Red'] },
    'Tablet': { hw: ['Pantalla Táctil', 'Batería', 'Cargador', 'Carcasa'], sw: ['SO', 'Apps Base'] },
    'Celulares': { hw: ['Pantalla Táctil', 'Batería', 'Cargador', 'Cámara'], sw: ['SO', 'Apps Base'] },
    'Audiovisuales': { hw: ['Cables', 'Conectores', 'Perillas'], sw: ['Firmware'] },
    'Sensores de humo': { hw: ['Batería', 'Cámara Óptica', 'Alarma Sonora'], sw: ['Conexión Panel'] },
    'UPS': { hw: ['Batería', 'Contactos', 'Panel Frontal'], sw: ['Software Monitoreo'] }
  };
  return config[tipo] || { hw: ['Estado Físico', 'Cables', 'Poder'], sw: ['Firmware', 'Configuración'] };
};

// --- COMPONENTE PRINCIPAL ---
export default function App() {
  const [activeModule, setActiveModule] = useState('none'); // 'none' (Portal), 'GET', 'FST14'
  const [currentScreen, setCurrentScreen] = useState('dashboard'); // 'dashboard', 'public_fst14', etc.
  const [currentUser, setCurrentUser] = useState(null);
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [equipos, setEquipos] = useState([]);
  
  // Estados de Interfaz Globales
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [sidebarColapsado, setSidebarColapsado] = useState(true);
  const [mensajeExito, setMensajeExito] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // Filtros de Identificación GET
  const [filtroIdentificar, setFiltroIdentificar] = useState('');
  const [filtroIdentificarUbicacion, setFiltroIdentificarUbicacion] = useState('');
  const [filtroIdentificarEstado, setFiltroIdentificarEstado] = useState('Todos');
  const [filtroIdentificarTipo, setFiltroIdentificarTipo] = useState('Todos');

  // Filtros de Seguimiento GET
  const [busqueda, setBusqueda] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('Todos');
  const [filtroTipo, setFiltroTipo] = useState('Todos');
  const [filtroUbicacionSeguimiento, setFiltroUbicacionSeguimiento] = useState('');

  // Estados de Modales GET
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [equipoEditando, setEquipoEditando] = useState(null);
  const [equipoAEliminar, setEquipoAEliminar] = useState(null);
  const [equipoEnRevision, setEquipoEnRevision] = useState(null);
  const [usuarioEditando, setUsuarioEditando] = useState(null);

  // Estados de Revisión Técnica GET
  const [hwRevision, setHwRevision] = useState({});
  const [swRevision, setSwRevision] = useState({ so: 'Windows 10', soOtro: '', configuracion: 'USB' });

  // ESTADOS FORMULARIOS DINÁMICOS RECUPERADOS (GET)
  const [tipoRegistro, setTipoRegistro] = useState('Computadores');
  const [formatoComputador, setFormatoComputador] = useState('Portátil');
  const [tvPlataformas, setTvPlataformas] = useState([]);
  const [usoTvForm, setUsoTvForm] = useState('Habitación');
  const [marcaImpresoraForm, setMarcaImpresoraForm] = useState('HP');
  const [tipoImpresoraForm, setTipoImpresoraForm] = useState('Láser');
  const [marcaTvForm, setMarcaTvForm] = useState('Samsung');
  const [marcaSwitchForm, setMarcaSwitchForm] = useState('Cisco');
  const [marcaApForm, setMarcaApForm] = useState('Ubiquiti');
  const [marcaPlantaForm, setMarcaPlantaForm] = useState('Mitel');
  const [marcaTelefonoIPForm, setMarcaTelefonoIPForm] = useState('Mitel');
  const [subtipoAudiovisualForm, setSubtipoAudiovisualForm] = useState('Amplificador');
  const [marcaTabletForm, setMarcaTabletForm] = useState('Samsung');
  const [marcaCelularForm, setMarcaCelularForm] = useState('Samsung');

  const [usuarios, setUsuarios] = useState([]);
  const [historialLogs, setHistorialLogs] = useState([]);

  // Estados Control ISO 9001
  const [mostrarModalVersion, setMostrarModalVersion] = useState(false);
  const [versionInfo, setVersionInfo] = useState({ version: '1.0', fecha: new Date().toISOString().split('T'), notas: 'Versión inicial del sistema' });

  // --- ESTADOS MÓDULO FST-14 ---
  const [fst14Tab, setFst14Tab] = useState('inbox'); // 'inbox', 'form'
  const [fst14Requests, setFst14Requests] = useState([]);
  const [viewingFst14, setViewingFst14] = useState(null);
  
  const [mostrarModalFst14Config, setMostrarModalFst14Config] = useState(false);
  const [fst14Config, setFst14Config] = useState({ formato: 'FST-14', version: '7', fecha: '16/08/2025' });

  const signatureCanvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  
  const defaultFst14Data = {
    tipoAccion: 'CREACIÓN',
    fecha: new Date().toISOString().split('T'),
    proceso: '',
    responsable: '',
    cargo: '',
    observaciones: '',
    usuarios: [{ id: Date.now(), identificacion: '', nombre: '', software: '', perfil: '' }]
  };
  const [fst14Data, setFst14Data] = useState(defaultFst14Data);

  const TIPOS_EQUIPO = [
    'Computadores', 'Impresoras', 'Televisores', 'Cámaras de seguridad', 'NVR / DVR', 'Planta Telefónica', 'Teléfonos IP', 'UPS', 'AP', 'Switch',
    'Sensores de humo', 'Audiovisuales', 'Tablet', 'Celulares', 'Otro'
  ];

  const ICONS_TIPO = {
    'Todos': <Box size={24} />,
    'Computadores': <Monitor size={24} />,
    'Impresoras': <Printer size={24} />,
    'Televisores': <Tv size={24} />,
    'Cámaras de seguridad': <Camera size={24} />,
    'NVR / DVR': <HardDrive size={24} />,
    'Planta Telefónica': <Phone size={24} />,
    'Teléfonos IP': <Phone size={24} />,
    'UPS': <Battery size={24} />,
    'AP': <Wifi size={24} />,
    'Switch': <Radio size={24} />,
    'Sensores de humo': <AlertTriangle size={24} />,
    'Audiovisuales': <Box size={24} />,
    'Tablet': <Tablet size={24} />,
    'Celulares': <Smartphone size={24} />,
    'Otro': <Box size={24} />
  };

  const defaultUsuarios = [
    { username: 'admin', pass: '1234', rol: 'Administrador', canCreate: true, canEdit: true, canDelete: true, canReview: true },
    { username: 'auxiliar', pass: '1234', rol: 'Auxiliar', canCreate: true, canEdit: true, canDelete: false, canReview: true },
    { username: 'visitante', pass: '1234', rol: 'Visitante', canCreate: false, canEdit: false, canDelete: false, canReview: false }
  ];

  // --- ESCUCHA DE RUTAS EXTERNAS (HASH) ---
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) {
        console.error("Error de autenticación:", err);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setFirebaseUser(user);
      setIsLoading(false);
    });
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!firebaseUser) return;

    const qEquipos = collection(db, 'artifacts', appId, 'public', 'data', 'equipos');
    const unsubscribeEquipos = onSnapshot(qEquipos, (snapshot) => {
      const docs = snapshot.docs.map(d => ({ id: d.id, ...d.data() }));
      setEquipos(docs.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0)));
    }, (err) => console.error("Error en equipos:", err));

    const qUsuarios = collection(db, 'artifacts', appId, 'public', 'data', 'usuarios');
    const unsubscribeUsuarios = onSnapshot(qUsuarios, (snapshot) => {
      const loaded = snapshot.docs.map(d => d.data());
      let merged = [...defaultUsuarios];
      loaded.forEach(lu => {
        const idx = merged.findIndex(du => du.username === lu.username);
        if (idx >= 0) merged[idx] = { ...merged[idx], ...lu };
        else merged.push(lu);
      });
      setUsuarios(merged);
      if (currentUser) {
        const fresh = merged.find(u => u.username === currentUser.username);
        if (fresh) setCurrentUser(fresh);
      }
    });

    const qHistorial = collection(db, 'artifacts', appId, 'public', 'data', 'historial');
    const unsubscribeHistorial = onSnapshot(qHistorial, (snapshot) => {
      setHistorialLogs(snapshot.docs.map(d => ({ id: d.id, ...d.data() })).sort((a, b) => b.timestamp - a.timestamp));
    });

    const qConfig = doc(db, 'artifacts', appId, 'public', 'data', 'config', 'versionInfo');
    const unsubscribeConfig = onSnapshot(qConfig, (docSnap) => {
      if (docSnap.exists()) {
        setVersionInfo(docSnap.data());
      }
    });

    const qFst14Config = doc(db, 'artifacts', appId, 'public', 'data', 'config', 'fst14Config');
    const unsubscribeFst14Config = onSnapshot(qFst14Config, (docSnap) => {
      if (docSnap.exists()) {
        setFst14Config(docSnap.data());
      }
    });

    const qFst14 = collection(db, 'artifacts', appId, 'public', 'data', 'fst14_solicitudes');
    const unsubscribeFst14 = onSnapshot(qFst14, (snapshot) => {
      setFst14Requests(snapshot.docs.map(d => ({ id: d.id, ...d.data() })).sort((a, b) => b.timestamp - a.timestamp));
    });

    return () => {
      unsubscribeEquipos();
      unsubscribeUsuarios();
      unsubscribeHistorial();
      unsubscribeConfig();
      unsubscribeFst14Config();
      unsubscribeFst14();
    };
  }, [firebaseUser, currentUser?.username]);

  // --- FUNCIONES AUXILIARES GLOBALES ---
  const toggleTvPlataforma = (plataforma) => {
    if (tvPlataformas.includes(plataforma)) {
      setTvPlataformas(tvPlataformas.filter(p => p !== plataforma));
    } else {
      setTvPlataformas([...tvPlataformas, plataforma]);
    }
  };

  // --- LÓGICA MÓDULO FST-14 Y FIRMA ---
  const handleFst14UserChange = (id, field, value) => {
    setFst14Data(prev => ({
      ...prev,
      usuarios: prev.usuarios.map(u => u.id === id ? { ...u, [field]: value } : u)
    }));
  };

  const addFst14User = () => {
    setFst14Data(prev => ({
      ...prev,
      usuarios: [...prev.usuarios, { id: Date.now(), identificacion: '', nombre: '', software: '', perfil: '' }]
    }));
  };

  const removeFst14User = (id) => {
    if (fst14Data.usuarios.length === 1) return;
    setFst14Data(prev => ({
      ...prev,
      usuarios: prev.usuarios.filter(u => u.id !== id)
    }));
  };

  const startDrawing = (e) => {
    const canvas = signatureCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches.clientX : e.clientX;
    const clientY = e.touches ? e.touches.clientY : e.clientY;
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#1e293b'; 
    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
  };

  const draw = (e) => {
    if (!isDrawing) return;
    const canvas = signatureCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches.clientX : e.clientX;
    const clientY = e.touches ? e.touches.clientY : e.clientY;
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => setIsDrawing(false);

  const clearSignature = () => {
    const canvas = signatureCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  const handleGuardarFST14 = async (e) => {
    e.preventDefault();
    if (!currentUser) return;
    
    const canvas = signatureCanvasRef.current;
    const signatureData = canvas ? canvas.toDataURL() : null;
    
    const docData = {
      ...fst14Data,
      firmaSolicitante: signatureData,
      creadoPor: currentUser.username,
      estadoSolicitud: 'Pendiente',
      timestamp: Date.now()
    };

    try {
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'fst14_solicitudes'), docData);
      
      await registrarHistorial('FST-14 Registrado', `Solicitud: ${fst14Data.tipoAccion}`, 'N/A', `Gestión de usuarios generada por ${currentUser.username}`, 'Usuarios', 'FST-14');
      
      setMensajeExito('Documento FST-14 guardado y enviado correctamente.');
      setFst14Data(defaultFst14Data);
      clearSignature();
      
      setTimeout(() => {
        setMensajeExito('');
        if (currentUser?.rol === 'Administrador') {
           setFst14Tab('inbox');
        }
      }, 3000);
    } catch (err) {
      console.error("Error al guardar FST-14:", err);
    }
  };

  const handleActualizarFst14Config = async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = {
      formato: form.formato.value,
      version: form.version.value,
      fecha: form.fecha.value
    };
    await setDoc(doc(db, 'artifacts', appId, 'public', 'data', 'config', 'fst14Config'), data);
    setMensajeExito('Configuración del formato FST-14 actualizada.');
    setMostrarModalFst14Config(false);
    setTimeout(() => setMensajeExito(''), 3000);
  };

  const renderFST14Form = () => (
    <div className="bg-white rounded-[2.5rem] border border-slate-200 shadow-2xl flex flex-col p-6 md:p-12 overflow-hidden relative">
      <div className="border-b-4 border-indigo-900 pb-6 mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative">
         <div className="text-center md:text-left flex-1 w-full">
           <div className="flex items-center justify-center md:justify-start gap-4 mb-2">
              <div className="w-12 h-12 bg-indigo-900 rounded-xl flex items-center justify-center text-white shrink-0"><ShieldCheck size={28}/></div>
              <h2 className="text-xl sm:text-2xl font-black text-indigo-900 tracking-tight leading-none">
                EM HOTELS <span className="text-slate-300 font-light mx-2">|</span> 
                <span className="text-sm sm:text-base text-slate-600 font-bold block sm:inline">CARTAGENA PLAZA</span>
              </h2>
           </div>
           <p className="text-[10px] font-black text-slate-400 tracking-widest uppercase">CARTAGENA DE INDIAS D.T. y C. - RNT.5286</p>
         </div>
         <div className="text-center md:text-right flex-1 w-full flex flex-col items-center md:items-end">
           <h3 className="text-lg md:text-xl font-black text-slate-800 mb-3">SOLICITUD DE CREACIÓN DE USUARIOS</h3>
           <div className="flex items-center gap-2">
             {currentUser?.rol === 'Administrador' && (
               <button type="button" onClick={() => setMostrarModalFst14Config(true)} className="p-2 px-3 bg-slate-50 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors border border-slate-200 shadow-sm flex items-center gap-2" title="Configurar Formato ISO 9001">
                 <Settings size={14}/> <span className="text-[10px] font-bold uppercase hidden sm:inline">Configurar</span>
               </button>
             )}
             <p className="text-xs font-black text-white bg-indigo-600 px-4 py-2 rounded-lg inline-block tracking-widest shadow-md m-0">
               {fst14Config.formato} V:{fst14Config.version} {fst14Config.fecha}
             </p>
           </div>
         </div>
      </div>

      <form onSubmit={handleGuardarFST14} className="space-y-8">
        <div className="flex flex-wrap justify-center gap-4 bg-slate-50 p-6 rounded-[2rem] border border-slate-200">
          {['CREACIÓN', 'MODIFICACIÓN', 'INACTIVACIÓN'].map(accion => (
            <label key={accion} className={`flex items-center gap-2 px-6 sm:px-8 py-3 sm:py-4 rounded-xl cursor-pointer font-black text-[10px] sm:text-xs uppercase tracking-widest transition-all ${fst14Data.tipoAccion === accion ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-200 scale-105' : 'bg-white text-slate-500 border border-slate-200 hover:bg-indigo-50 hover:text-indigo-600'}`}>
              <input type="radio" name="tipoAccion" value={accion} checked={fst14Data.tipoAccion === accion} onChange={(e) => setFst14Data({...fst14Data, tipoAccion: e.target.value})} className="hidden" />
              {accion === 'CREACIÓN' && <UserPlus size={16}/>}
              {accion === 'MODIFICACIÓN' && <PenTool size={16}/>}
              {accion === 'INACTIVACIÓN' && <Trash2 size={16}/>}
              {accion}
            </label>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-white">
          <div><label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Fecha</label><input type="date" value={fst14Data.fecha} onChange={(e) => setFst14Data({...fst14Data, fecha: e.target.value})} required className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-200 focus:border-indigo-400 outline-none font-bold text-slate-700 transition-colors" /></div>
          <div><label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Proceso</label><input type="text" value={fst14Data.proceso} onChange={(e) => setFst14Data({...fst14Data, proceso: e.target.value})} required placeholder="Ej: Recepción, Contabilidad..." className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-200 focus:border-indigo-400 outline-none font-bold text-slate-700 transition-colors" /></div>
          <div><label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Responsable</label><input type="text" value={fst14Data.responsable} onChange={(e) => setFst14Data({...fst14Data, responsable: e.target.value})} required placeholder="Nombre completo del solicitante" className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-200 focus:border-indigo-400 outline-none font-bold text-slate-700 transition-colors" /></div>
          <div><label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Cargo</label><input type="text" value={fst14Data.cargo} onChange={(e) => setFst14Data({...fst14Data, cargo: e.target.value})} required placeholder="Cargo del solicitante" className="w-full p-4 rounded-2xl bg-slate-50 border border-slate-200 focus:border-indigo-400 outline-none font-bold text-slate-700 transition-colors" /></div>
        </div>

        <div className="border-2 border-slate-200 rounded-[2rem] overflow-hidden bg-white shadow-sm">
           <div className="overflow-x-auto scrollbar-thin">
             <table className="w-full text-left min-w-[800px]">
               <thead className="bg-slate-50 border-b border-slate-200">
                 <tr>
                   <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest w-1/4">Identificación</th>
                   <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest w-1/3">Nombre y Apellidos</th>
                   <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Software o Aplicativo</th>
                   <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Perfil</th>
                   <th className="px-4 py-4 w-12 text-center"><Settings size={14} className="text-slate-400 mx-auto"/></th>
                 </tr>
               </thead>
               <tbody className="divide-y divide-slate-100">
                 {fst14Data.usuarios.map((u, i) => (
                   <tr key={u.id} className="hover:bg-indigo-50/30 transition-colors">
                     <td className="p-3"><input type="text" value={u.identificacion} onChange={(e) => handleFst14UserChange(u.id, 'identificacion', e.target.value)} required placeholder="C.C / NIT" className="w-full p-3 bg-slate-50 border border-slate-200 outline-none font-bold text-sm focus:border-indigo-400 rounded-xl transition-colors" /></td>
                     <td className="p-3"><input type="text" value={u.nombre} onChange={(e) => handleFst14UserChange(u.id, 'nombre', e.target.value)} required placeholder="Nombre completo del usuario" className="w-full p-3 bg-slate-50 border border-slate-200 outline-none font-bold text-sm focus:border-indigo-400 rounded-xl transition-colors" /></td>
                     <td className="p-3"><input type="text" value={u.software} onChange={(e) => handleFst14UserChange(u.id, 'software', e.target.value)} required placeholder="Ej: Zeus, Windows" className="w-full p-3 bg-slate-50 border border-slate-200 outline-none font-bold text-sm focus:border-indigo-400 rounded-xl transition-colors" /></td>
                     <td className="p-3"><input type="text" value={u.perfil} onChange={(e) => handleFst14UserChange(u.id, 'perfil', e.target.value)} required placeholder="Ej: Admin, Cajero" className="w-full p-3 bg-slate-50 border border-slate-200 outline-none font-bold text-sm focus:border-indigo-400 rounded-xl transition-colors" /></td>
                     <td className="p-3 text-center">
                       <button type="button" onClick={() => removeFst14User(u.id)} disabled={fst14Data.usuarios.length === 1} className="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-lg transition-colors disabled:opacity-30 disabled:hover:bg-transparent"><Trash2 size={18}/></button>
                     </td>
                   </tr>
                 ))}
               </tbody>
             </table>
           </div>
           <div className="bg-slate-50 p-4 border-t border-slate-200">
             <button type="button" onClick={addFst14User} className="text-xs font-black text-indigo-600 uppercase tracking-widest flex items-center gap-2 hover:text-indigo-800 transition-colors bg-white px-4 py-3 rounded-xl border border-indigo-100 shadow-sm active:scale-95">
               <Plus size={16}/> Agregar Usuario Adicional
             </button>
           </div>
        </div>

        <div>
          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1 flex items-center gap-2"><FileText size={14}/> Observaciones</label>
          <textarea value={fst14Data.observaciones} onChange={(e) => setFst14Data({...fst14Data, observaciones: e.target.value})} rows="3" placeholder="Detalle cualquier requerimiento adicional (opcional)..." className="w-full p-5 rounded-2xl bg-slate-50 border border-slate-200 focus:border-indigo-400 outline-none font-medium text-slate-700 resize-none mt-2 transition-colors"></textarea>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-4 pt-8 border-t-2 border-slate-100">
          <div className="bg-slate-50 p-6 rounded-3xl border border-slate-200">
             <p className="text-[10px] font-black text-indigo-600 uppercase tracking-widest mb-4 flex items-center gap-2"><PenTool size={14}/> Gestor y/o Líder del Proceso</p>
             <div className="border-2 border-dashed border-indigo-200 rounded-2xl overflow-hidden bg-white relative group shadow-inner">
                <canvas 
                  ref={signatureCanvasRef} 
                  width={400} 
                  height={150} 
                  className="w-full h-[150px] cursor-crosshair touch-none"
                  onMouseDown={startDrawing}
                  onMouseMove={draw}
                  onMouseUp={stopDrawing}
                  onMouseLeave={stopDrawing}
                  onTouchStart={startDrawing}
                  onTouchMove={draw}
                  onTouchEnd={stopDrawing}
                />
                <div className="absolute inset-0 pointer-events-none flex items-center justify-center opacity-30 group-hover:opacity-10 transition-opacity">
                  <span className="font-black text-2xl md:text-3xl text-indigo-300 -rotate-6 tracking-widest">FIRME AQUÍ</span>
                </div>
                <button type="button" onClick={clearSignature} className="absolute bottom-3 right-3 bg-slate-100 border border-slate-200 text-[10px] px-3 py-2 rounded-xl shadow-sm text-slate-500 hover:text-rose-600 hover:bg-rose-50 flex items-center gap-1 font-black uppercase tracking-widest transition-all">
                  Limpiar
                </button>
             </div>
             <div className="mt-4 pt-4 border-t border-slate-200">
               <p className="font-black text-sm text-slate-800 uppercase truncate">{fst14Data.responsable || 'NOMBRE DEL SOLICITANTE'}</p>
               <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1 truncate">{fst14Data.cargo || 'CARGO DEL SOLICITANTE'}</p>
             </div>
          </div>
          
          <div className="bg-slate-50 p-6 rounded-3xl border border-slate-200">
             <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Gestor de Sistemas e Innovación</p>
             <div className="border-2 border-slate-200 rounded-2xl h-[150px] bg-white flex items-center justify-center relative overflow-hidden shadow-inner">
                <div className="flex flex-col items-center justify-center">
                  <ShieldCheck size={40} className="text-slate-300 mb-2" />
                  <span className="font-black text-sm text-slate-400 uppercase tracking-widest text-center">Espacio Reservado</span>
                  <span className="text-[10px] font-bold text-slate-400 mt-1 text-center">Para aprobación posterior</span>
                </div>
             </div>
             <div className="mt-4 pt-4 border-t border-slate-200">
               <p className="font-black text-sm text-slate-800 uppercase">HAROLD DE LA ESPRIELLA VEGA</p>
               <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">GESTOR DE SISTEMAS E INNOVACIÓN</p>
             </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-end gap-4 pt-8 border-t border-slate-200">
           <button type="submit" className="bg-indigo-600 text-white font-black uppercase tracking-widest text-sm px-10 py-5 rounded-full shadow-xl shadow-indigo-200 hover:bg-indigo-700 active:scale-95 transition-all flex items-center justify-center gap-3">
             <FileSignature size={20}/> Procesar Solicitud
           </button>
        </div>
      </form>
    </div>
  );

  // --- FUNCIONES DE ACCIÓN GET ---
  const registrarHistorial = async (accion, equipoNombre, equipoId, detalles, equipoTipo = 'Desconocido', seccion = 'General') => {
    if (!currentUser) return;
    try {
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'historial'), {
        accion, equipoNombre, equipoId, detalles, equipoTipo, seccion,
        usuario: currentUser.username, rol: currentUser.rol, timestamp: Date.now()
      });
    } catch (e) { console.error("Error historial:", e); }
  };

  const handleRegistrarEquipo = async (e) => {
    e.preventDefault();
    if (!currentUser?.canCreate && currentUser?.rol !== 'Administrador') return;

    const form = e.target;
    let fotoBase64 = null;
    
    if (form.foto && form.foto.files && form.foto.files.length > 0) {
      const reader = new FileReader();
      fotoBase64 = await new Promise(r => {
        reader.onload = (ev) => r(ev.target.result);
        reader.readAsDataURL(form.foto.files);
      });
    }

    let descripcionAutomatica = 'Sin descripción';
    let ubicacionFinal = form.ubicacion?.value || 'N/A';
    
    if (tipoRegistro === 'Computadores') {
      const monitorStr = form.formatoComputador.value === 'Torre' && form.incluyeMonitor ? ` (+Monitor: ${form.incluyeMonitor.value})` : '';
      descripcionAutomatica = `Fmt: ${form.formatoComputador.value}${monitorStr} | CPU: ${form.procesador?.value} | RAM: ${form.ram?.value} ${form.tipoRam?.value} | Disco: ${form.disco?.value} ${form.tipoDisco?.value} | SO: ${form.so?.value}`;
    } else if (tipoRegistro === 'Impresoras') {
      const marca = marcaImpresoraForm === 'Otro' ? form.marcaImpresoraOtro?.value : marcaImpresoraForm;
      const tipoImp = tipoImpresoraForm === 'Otro' ? form.tipoImpresoraOtro?.value : tipoImpresoraForm;
      descripcionAutomatica = `Marca: ${marca} | Mod: ${form.modeloImpresora?.value} | Tipo: ${tipoImp} | Tóner: ${form.toner?.value} | Prov: ${form.esDeProveedor?.value}`;
    } else if (tipoRegistro === 'Televisores') {
      const marca = marcaTvForm === 'Otro' ? form.marcaTvOtro?.value : marcaTvForm;
      const apps = tvPlataformas.length > 0 ? ` | Apps: ${tvPlataformas.join(', ')}` : '';
      descripcionAutomatica = `Uso: ${usoTvForm} | Marca: ${marca} | Mod: ${form.modeloTv?.value} | ${form.tamanoTv?.value}" | Smart: ${form.smartTv?.value} | Claro: ${form.decodClaro?.value} | DTV: ${form.directTv?.value} | Controles: ${form.cantidadControles?.value}${apps}`;
      ubicacionFinal = usoTvForm === 'Habitación' ? `Habitación ${form.detalleUbicacionTv?.value}` : usoTvForm === 'Pantalla Publicitaria' ? `Piso ${form.detalleUbicacionTv?.value} (Pantalla)` : `Oficina: ${form.detalleUbicacionTv?.value}`;
    } else if (tipoRegistro === 'AP') {
      const marca = marcaApForm === 'Otro' ? form.marcaApOtro?.value : marcaApForm;
      descripcionAutomatica = `Marca: ${marca} | Mod: ${form.modeloAp?.value}`;
      ubicacionFinal = `Piso ${form.pisoAp?.value} - AP-${form.numAp?.value} (${form.sectorAp?.value})`;
    } else if (tipoRegistro === 'Switch') {
      const marca = marcaSwitchForm === 'Otro' ? form.marcaSwitchOtro?.value : marcaSwitchForm;
      descripcionAutomatica = `Marca: ${marca} | Mod: ${form.modeloSwitch?.value} | Puertos: ${form.puertosSwitch?.value} | PoE: ${form.poeSwitch?.value}`;
    } else if (tipoRegistro === 'Planta Telefónica') {
      const marca = marcaPlantaForm === 'Otro' ? form.marcaPlantaOtro?.value : marcaPlantaForm;
      descripcionAutomatica = `Marca: ${marca} | Tipo: ${form.tipoPlanta?.value} | Exts: ${form.extensionesPlanta?.value}`;
    } else if (tipoRegistro === 'Teléfonos IP') {
      const marca = marcaTelefonoIPForm === 'Otro' ? form.marcaTelefonoIPOtro?.value : marcaTelefonoIPForm;
      descripcionAutomatica = `Marca: ${marca} | Mod: ${form.modeloTelefonoIP?.value} | Ext: ${form.extensionTelefonoIP?.value} | PoE: ${form.poeTelefonoIP?.value}`;
    } else if (tipoRegistro === 'NVR / DVR') {
      descripcionAutomatica = `Tipo: ${form.tipoNvr?.value} | Canales: ${form.canalesNvr?.value} | Disco: ${form.discoNvr?.value}`;
    } else if (tipoRegistro === 'Cámaras de seguridad') {
      descripcionAutomatica = `Formato: ${form.tipoCamara?.value} | Tec: ${form.tecnologiaCamara?.value} | Conectada a: ${form.nvrDvr?.value}`;
    } else if (tipoRegistro === 'Audiovisuales') {
      const subtipo = subtipoAudiovisualForm === 'Otro' ? form.subtipoAudiovisualOtro?.value : subtipoAudiovisualForm;
      descripcionAutomatica = `Disp: ${subtipo} | Marca: ${form.marcaAudiovisual?.value} | Mod: ${form.modeloAudiovisual?.value}`;
    } else if (tipoRegistro === 'Tablet') {
      const marca = marcaTabletForm === 'Otro' ? form.marcaTabletOtro?.value : marcaTabletForm;
      descripcionAutomatica = `Marca: ${marca} | Mod: ${form.modeloTablet?.value} | ${form.tamanoTablet?.value} | CPU: ${form.procesadorTablet?.value} | RAM: ${form.ramTablet?.value} | ROM: ${form.almacenamientoTablet?.value} | Forro: ${form.forroTablet?.value} | Vidrio: ${form.vidrioTablet?.value} | Email: ${form.emailDispositivo?.value||'N/A'} | Cel: ${form.numeroCelular?.value||'N/A'}`;
    } else if (tipoRegistro === 'Celulares') {
      const marca = marcaCelularForm === 'Otro' ? form.marcaCelularOtro?.value : marcaCelularForm;
      descripcionAutomatica = `Marca: ${marca} | Mod: ${form.modeloCelular?.value} | ${form.tamanoCelular?.value} | CPU: ${form.procesadorCelular?.value} | RAM: ${form.ramCelular?.value} | ROM: ${form.almacenamientoCelular?.value} | Forro: ${form.forroCelular?.value} | Vidrio: ${form.vidrioCelular?.value} | Email: ${form.emailDispositivo?.value||'N/A'} | Cel: ${form.numeroCelular?.value||'N/A'}`;
    } else if (tipoRegistro === 'Otro') {
      descripcionAutomatica = form.descripcionOtro?.value || 'Sin descripción';
    }

    const nuevoEquipo = {
      codigo: form.codigo.value,
      nombre: form.nombre.value,
      tipo: tipoRegistro,
      ubicacion: ubicacionFinal,
      serie: form.serie?.value || 'S/N',
      ip: form.ip?.value || 'N/A',
      mac: form.mac?.value || 'N/A',
      estado: form.estado.value,
      tieneQR: form.tieneQR.value,
      responsable: form.responsable?.value || 'N/A',
      descripcion: String(descripcionAutomatica),
      foto: fotoBase64,
      timestamp: Date.now()
    };

    try {
      const docRef = await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'equipos'), nuevoEquipo);
      await registrarHistorial('Creación', nuevoEquipo.nombre, docRef.id, 'Registro inicial detallado.', nuevoEquipo.tipo, 'Identificación');
      setMensajeExito("¡Equipo registrado con éxito!");
      setMostrarFormulario(false);
      setTvPlataformas([]); 
      setTimeout(() => setMensajeExito(''), 3000);
    } catch (err) { console.error("Error al registrar:", err); }
  };

  const handleActualizarEquipo = async (e) => {
    e.preventDefault();
    if (!equipoEditando) return;
    const form = e.target;
    const updateData = {
      codigo: form.codigo.value,
      nombre: form.nombre.value,
      ubicacion: form.ubicacion.value,
      estado: form.estado.value,
      responsable: form.responsable?.value || 'N/A',
      tieneQR: form.tieneQR.value
    };
    await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', 'equipos', equipoEditando.id), updateData);
    await registrarHistorial('Edición', updateData.nombre, equipoEditando.id, 'Actualización técnica.', equipoEditando.tipo, 'Identificación');
    setEquipoEditando(null);
    setMensajeExito("Datos actualizados correctamente.");
    setTimeout(() => setMensajeExito(''), 3000);
  };

  const handleEliminarEquipo = async () => {
    if (!equipoAEliminar) return;
    await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', 'equipos', equipoAEliminar.id));
    await registrarHistorial('Eliminación', equipoAEliminar.nombre, equipoAEliminar.id, 'Baja del sistema.', equipoAEliminar.tipo, 'Identificación');
    setEquipoAEliminar(null);
    setMensajeExito("Equipo eliminado.");
    setTimeout(() => setMensajeExito(''), 3000);
  };

  const handleActualizarPermisos = async (e) => {
    e.preventDefault();
    if (!usuarioEditando) return;
    const data = {
      username: usuarioEditando.username,
      rol: e.target.rol.value,
      canCreate: e.target.canCreate.checked,
      canEdit: e.target.canEdit.checked,
      canDelete: e.target.canDelete.checked,
      canReview: e.target.canReview.checked,
      timestamp: Date.now()
    };
    await setDoc(doc(db, 'artifacts', appId, 'public', 'data', 'usuarios', usuarioEditando.username), data, { merge: true });
    setMensajeExito(`Permisos de ${usuarioEditando.username} actualizados.`);
    setUsuarioEditando(null);
    setTimeout(() => setMensajeExito(''), 3000);
  };

  const handleActualizarVersion = async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = {
      version: form.version.value,
      fecha: form.fecha.value,
      notas: form.notas.value,
      timestamp: Date.now(),
      actualizadoPor: currentUser.username
    };
    await setDoc(doc(db, 'artifacts', appId, 'public', 'data', 'config', 'versionInfo'), data);
    await registrarHistorial('Actualización ISO 9001', `Versión ${data.version}`, 'N/A', `Control de cambios GET: ${data.notas}`, 'Sistema', 'Configuración');
    setMensajeExito('Control de versiones (ISO 9001) actualizado.');
    setMostrarModalVersion(false);
    setTimeout(() => setMensajeExito(''), 3000);
  };

  const generarDatosDePrueba = async () => {
    if (!currentUser || currentUser.rol !== 'Administrador') return;
    setIsLoading(true);
    try {
      const mockData = [
        { codigo: 'PC-001', nombre: 'Laptop Gerencia', tipo: 'Computadores', ubicacion: 'Oficina Gerencia', serie: 'SN-X98765', ip: '192.168.1.15', mac: '00:1B:44:11:3A:B7', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'Carlos Perez', descripcion: 'Fmt: Portátil | CPU: Intel Core i7 | RAM: 16GB DDR4 | Disco: 512GB SSD NVMe | SO: Windows 11', timestamp: Date.now() - 10000 },
        { codigo: 'IMP-001', nombre: 'Impresora Contabilidad', tipo: 'Impresoras', ubicacion: 'Área Contable', serie: 'BR-4455', ip: '192.168.1.20', mac: 'N/A', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'N/A', descripcion: 'Marca: HP | Mod: LaserJet Pro | Tipo: Láser | Tóner: CF258A | Prov: Sí', timestamp: Date.now() - 20000 },
        { codigo: 'TV-001', nombre: 'TV Sala de Juntas', tipo: 'Televisores', ubicacion: 'Sala de Juntas Piso 2', serie: 'SNG-8899', ip: '192.168.1.45', mac: 'N/A', estado: 'Activo', tieneQR: 'No', responsable: 'TI', descripcion: 'Uso: Oficina | Marca: Samsung | Mod: Crystal UHD | 65" | Smart: Sí | Claro: No | DTV: No | Controles: 1 | Apps: Netflix, Youtube', timestamp: Date.now() - 30000 },
        { codigo: 'AP-001', nombre: 'AP Pasillo Sur', tipo: 'AP', ubicacion: 'Piso 2 - AP-1 (Pasillo Sur)', serie: 'UB-1122', ip: '192.168.1.5', mac: 'AA:BB:CC:DD:EE', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'TI', descripcion: 'Marca: Ubiquiti | Mod: UniFi 6 Lite', timestamp: Date.now() - 40000 },
        { codigo: 'CEL-001', nombre: 'Celular Corporativo Ventas', tipo: 'Celulares', ubicacion: 'Ventas en Calle', serie: 'IMEI-99887766', ip: 'N/A', mac: 'N/A', estado: 'En Reparación', tieneQR: 'No', responsable: 'Ana Gomez', descripcion: 'Marca: Samsung | Mod: Galaxy S23 | 6.1" | CPU: Snapdragon | RAM: 8GB | ROM: 256GB | Forro: Sí | Vidrio: Sí | Email: ana@empresa.com | Cel: 3001234567', novedad: 'Pantalla astillada, requiere cambio de display', timestamp: Date.now() - 50000 },
        { codigo: 'CAM-001', nombre: 'Cámara Recepción', tipo: 'Cámaras de seguridad', ubicacion: 'Recepción Principal', serie: 'HK-12345', ip: '192.168.1.50', mac: 'N/A', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'Seguridad', descripcion: 'Formato: Domo | Tec: IP / Red | Conectada a: NVR Principal', timestamp: Date.now() - 60000 },
        { codigo: 'NVR-001', nombre: 'Grabador Principal', tipo: 'NVR / DVR', ubicacion: 'Cuarto de Control', serie: 'NVR-999', ip: '192.168.1.10', mac: 'N/A', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'Seguridad', descripcion: 'Tipo: NVR (Red/IP) | Canales: 32 | Disco: 8TB', timestamp: Date.now() - 70000 },
        { codigo: 'PT-001', nombre: 'Planta PBX', tipo: 'Planta Telefónica', ubicacion: 'Rack Comunicaciones', serie: 'MT-888', ip: '192.168.1.2', mac: 'N/A', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'TI', descripcion: 'Marca: Mitel | Tipo: IP (VoIP) | Exts: 50', timestamp: Date.now() - 80000 },
        { codigo: 'TEL-102', nombre: 'Teléfono Gerencia', tipo: 'Teléfonos IP', ubicacion: 'Oficina Gerencia', serie: 'YL-456', ip: '192.168.1.102', mac: 'N/A', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'Carlos Perez', descripcion: 'Marca: Yealink | Mod: SIP-T46U | Ext: 102 | PoE: Sí (PoE)', timestamp: Date.now() - 90000 },
        { codigo: 'UPS-001', nombre: 'UPS Rack Principal', tipo: 'UPS', ubicacion: 'Rack Comunicaciones', serie: 'APC-111', ip: '192.168.1.3', mac: 'N/A', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'TI', descripcion: 'Capacidad 3KVA, Topología On-Line Doble Conversión', timestamp: Date.now() - 100000 },
        { codigo: 'SW-001', nombre: 'Switch Core', tipo: 'Switch', ubicacion: 'Rack Comunicaciones', serie: 'CS-2960', ip: '192.168.1.4', mac: 'N/A', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'TI', descripcion: 'Marca: Cisco | Mod: SG350 | Puertos: 24 | PoE: Sí', timestamp: Date.now() - 110000 },
        { codigo: 'SMK-001', nombre: 'Sensor Humo Pasillo', tipo: 'Sensores de humo', ubicacion: 'Pasillo Piso 2', serie: 'N/A', ip: 'N/A', mac: 'N/A', estado: 'Funcionando', tieneQR: 'No', responsable: 'Mantenimiento', descripcion: 'Sensor óptico de humo direccionable', timestamp: Date.now() - 120000 },
        { codigo: 'AV-001', nombre: 'Proyector Sala Juntas', tipo: 'Audiovisuales', ubicacion: 'Sala de Juntas Piso 2', serie: 'EP-777', ip: '192.168.1.60', mac: 'N/A', estado: 'Activo', tieneQR: 'Sí', responsable: 'TI', descripcion: 'Disp: Proyector | Marca: Epson | Mod: PowerLite', timestamp: Date.now() - 130000 },
        { codigo: 'TAB-001', nombre: 'Tablet Encuestas', tipo: 'Tablet', ubicacion: 'Recepción', serie: 'IPD-333', ip: 'N/A', mac: 'N/A', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'Recepción', descripcion: 'Marca: Apple (iPad) | Mod: iPad Pro | 11" | CPU: Apple M-Series | RAM: 8GB | ROM: 256GB | Forro: Sí | Vidrio: Sí | Email: recepcion@empresa.com | Cel: N/A', timestamp: Date.now() - 140000 },
        { codigo: 'OTR-001', nombre: 'Reloj Biométrico', tipo: 'Otro', ubicacion: 'Entrada Personal', serie: 'ZK-001', ip: '192.168.1.70', mac: 'N/A', estado: 'Funcionando', tieneQR: 'Sí', responsable: 'RRHH', descripcion: 'Control de acceso facial y dactilar ZKTeco', timestamp: Date.now() - 150000 }
      ];
      for (const eq of mockData) {
        await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'equipos'), eq);
      }
      await registrarHistorial('Sistema', 'Generación Automática', 'N/A', 'Se generaron 15 equipos de prueba en la base de datos.', 'Sistema', 'Configuración');
      setMensajeExito('Se han inyectado datos de prueba al sistema.');
    } catch (error) {
      console.error('Error insertando datos de prueba:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAbrirRevision = (equipo) => {
    if (equipo) {
      const { hw, sw } = getChecklistItems(equipo.tipo);
      
      let hws = {};
      hw.forEach(i => {
        hws[i] = (typeof equipo.hardware === 'string' && equipo.hardware.includes(`${i}: ✖ `)) ? ' ✖ ' : ' ✔ ';
      });
      
      let sws = {};
      sw.forEach(i => {
        if (i !== 'SO' && i !== 'Configuración') {
          sws[i] = (typeof equipo.software === 'string' && equipo.software.includes(`${i}: ✖ `)) ? ' ✖ ' : ' ✔ ';
        }
      });

      let parsedSo = ['Tablet', 'Celulares'].includes(equipo.tipo) ? 'Android' : 'Windows 10';
      let parsedSoOtro = '';
      let parsedConfiguracion = 'USB';
      
      const swStr = typeof equipo.software === 'string' ? equipo.software : '';
      if (swStr.includes('SO:')) {
        const partes = swStr.split('|');
        const soParte = partes.find(p => p.trim().startsWith('SO:'));
        if (soParte) {
          const soVal = soParte.replace('SO:', '').trim();
          if (['Windows 10', 'Windows 11', 'macOS', 'Android', 'iOS'].includes(soVal)) {
            parsedSo = soVal;
          } else {
            parsedSo = 'Otro';
            parsedSoOtro = soVal;
          }
        }
      }
      
      if (swStr.includes('Configuración:')) {
        const partes = swStr.split('|');
        const configParte = partes.find(p => p.trim().startsWith('Configuración:'));
        if (configParte) {
          parsedConfiguracion = configParte.replace('Configuración:', '').trim();
        }
      }

      setHwRevision(hws);
      setSwRevision({...sws, so: parsedSo, soOtro: parsedSoOtro, configuracion: parsedConfiguracion});
    }
    setEquipoEnRevision(equipo);
  };

  const handleGuardarRevision = async (e) => {
    e.preventDefault();
    if (!equipoEnRevision) return;
    const form = e.target;
    const fecha = form.fechaRevision.value;
    
    const { hw, sw } = getChecklistItems(equipoEnRevision.tipo);
    const hardwareStr = hw.map(item => `${item}:${hwRevision[item] || ' ✔ '}`).join(' | ');
    
    let swArr = [];
    if (sw.includes('SO')) {
      const soFinal = swRevision.so === 'Otro' ? (swRevision.soOtro || 'Otro') : swRevision.so;
      swArr.push(`SO:${soFinal}`);
    }
    if (sw.includes('Configuración')) {
      swArr.push(`Configuración:${swRevision.configuracion || 'USB'}`);
    }
    sw.forEach(item => {
      if (item !== 'SO' && item !== 'Configuración') swArr.push(`${item}:${swRevision[item] || ' ✔ '}`);
    });
    const softwareStr = swArr.join(' | ');
    
    const updateData = {
      ultimaInspeccion: String(fecha),
      estado: form.estado.value,
      novedad: String(form.novedad.value || 'Sin novedades'),
      hardware: String(hardwareStr),
      software: String(softwareStr),
      odt: String(form.odt?.value || 'No'),
      numeroOdt: String(form.numeroOdt?.value || '')
    };

    await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', 'equipos', equipoEnRevision.id), updateData);
    await registrarHistorial('Seguimiento', equipoEnRevision.nombre, equipoEnRevision.id, `Revisión: ${updateData.estado}.`, equipoEnRevision.tipo, 'Seguimiento');
    setEquipoEnRevision(null);
    setMensajeExito("Seguimiento guardado.");
    setTimeout(() => setMensajeExito(''), 3000);
  };

  const filteredEquipos = useMemo(() => {
    return equipos.filter(eq => {
      const eqNombre = eq.nombre ? String(eq.nombre).toLowerCase() : '';
      const eqCodigo = eq.codigo ? String(eq.codigo).toLowerCase() : '';
      const eqUbicacion = eq.ubicacion ? String(eq.ubicacion).toLowerCase() : '';
      
      const matchText = eqNombre.includes(filtroIdentificar.toLowerCase()) || eqCodigo.includes(filtroIdentificar.toLowerCase());
      const matchTipo = filtroIdentificarTipo === 'Todos' || eq.tipo === filtroIdentificarTipo;
      const matchEstado = filtroIdentificarEstado === 'Todos' || eq.estado === filtroIdentificarEstado;
      const matchUb = !filtroIdentificarUbicacion || eqUbicacion.includes(filtroIdentificarUbicacion.toLowerCase());
      
      return matchText && matchTipo && matchEstado && matchUb;
    });
  }, [equipos, filtroIdentificar, filtroIdentificarTipo, filtroIdentificarEstado, filtroIdentificarUbicacion]);

  const getEstadoClasses = (estado) => {
    const classes = {
      'Funcionando': 'bg-emerald-50 text-emerald-700 border-emerald-200',
      'Activo': 'bg-blue-50 text-blue-700 border-blue-200',
      'En Reparación': 'bg-amber-50 text-amber-700 border-amber-200',
      'Inactivo': 'bg-slate-100 text-slate-700 border-slate-200',
      'De Baja': 'bg-rose-50 text-rose-700 border-rose-200'
    };
    return classes[estado] || 'bg-gray-50 text-gray-700 border-gray-200';
  };

  // --- RENDERS ---
  if (isLoading) return (
    <div className="h-screen flex flex-col items-center justify-center bg-slate-50">
      <div className="animate-spin text-blue-600 mb-4"><Wifi size={48} /></div>
      <p className="text-slate-500 font-bold animate-pulse">Cargando Plataforma...</p>
    </div>
  );

  // 1. PORTAL DE APLICACIONES (LAUNCHER PRINCIPAL - SIN LOGIN REQUERIDO)
  if (activeModule === 'none') {
    return (
      <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8 shadow-sm">
          <div className="flex items-center gap-3">
            <Grid size={24} className="text-blue-600" />
            <h1 className="text-xl font-black text-slate-800">Portal Corporativo EM Hotels</h1>
          </div>
          {/* Si ya hay usuario logueado, muestra la info y botón de salir, de lo contrario nada */}
          {currentUser && (
             <div className="flex items-center gap-4">
               <div className="text-right hidden sm:block">
                  <p className="text-sm font-black text-slate-800 uppercase leading-none">{safeStr(currentUser?.username)}</p>
                  <p className="text-[10px] font-bold text-blue-600 uppercase mt-1 tracking-widest">{safeStr(currentUser?.rol)}</p>
               </div>
               <button onClick={() => { setCurrentUser(null); setActiveModule('none'); }} className="p-2 bg-rose-50 text-rose-500 rounded-xl hover:bg-rose-100 transition-colors" title="Cerrar Sesión">
                 <LogOut size={20} />
               </button>
             </div>
          )}
        </header>

        <main className="flex-1 flex items-center justify-center p-8 animate-in fade-in duration-500">
          <div className="max-w-4xl w-full">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-black text-slate-800 tracking-tighter mb-2">Selecciona un Módulo</h2>
              <p className="text-slate-500 font-medium text-lg">Catálogo de aplicaciones corporativas a tu disposición.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* CARD 1: SISTEMA GET (PRIVADO) */}
              <button 
                onClick={() => { setActiveModule('GET'); setCurrentScreen('dashboard'); }}
                className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-xl hover:shadow-2xl hover:border-blue-400 transition-all text-left group relative overflow-hidden flex flex-col"
              >
                <div className="absolute -right-10 -top-10 w-40 h-40 bg-blue-50 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                <div className="relative z-10 flex-1">
                  <div className="w-14 h-14 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors shadow-inner">
                    <Monitor size={28} />
                  </div>
                  <h3 className="text-2xl font-black text-slate-800 mb-3 tracking-tight">Sistema GET</h3>
                  <p className="text-slate-500 text-sm font-medium leading-relaxed">
                    Gestión de Equipos Tecnológicos. Control de inventarios, averías y mantenimientos.
                  </p>
                </div>
                <div className="relative z-10 mt-6 pt-4 border-t border-slate-100 w-full text-center">
                  <span className="text-[10px] font-black uppercase tracking-widest text-blue-600 bg-blue-50 px-3 py-1.5 rounded-lg">Módulo Privado</span>
                </div>
              </button>

              {/* CARD 2: GESTIÓN FST-14 (PRIVADO) */}
              <button 
                onClick={() => { setActiveModule('FST14'); }}
                className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-xl hover:shadow-2xl hover:border-indigo-400 transition-all text-left group relative overflow-hidden flex flex-col"
              >
                <div className="absolute -right-10 -top-10 w-40 h-40 bg-indigo-50 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                <div className="relative z-10 flex-1">
                  <div className="w-14 h-14 bg-indigo-100 text-indigo-600 rounded-2xl flex items-center justify-center mb-6 group-hover:bg-indigo-600 group-hover:text-white transition-colors shadow-inner">
                    <UserPlus size={28} />
                  </div>
                  <h3 className="text-2xl font-black text-slate-800 mb-3 tracking-tight">Módulo FST-14</h3>
                  <p className="text-slate-500 text-sm font-medium leading-relaxed">
                    Gestión y control de usuarios. Solicita accesos y aprueba formatos oficiales del hotel.
                  </p>
                </div>
                <div className="relative z-10 mt-6 pt-4 border-t border-slate-100 w-full text-center">
                  <span className="text-[10px] font-black uppercase tracking-widest text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-lg">Módulo Corporativo</span>
                </div>
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // 2. PANTALLA DE LOGIN (SE MUESTRA AL ELEGIR UN MÓDULO PRIVADO Y NO ESTAR LOGUEADO)
  if (!currentUser && (activeModule === 'GET' || activeModule === 'FST14')) {
    const isGet = activeModule === 'GET';
    const ModIcon = isGet ? Monitor : Inbox;
    const colorBg = isGet ? 'bg-blue-600' : 'bg-indigo-600';
    const colorHover = isGet ? 'hover:border-blue-400' : 'hover:border-indigo-400';
    const colorHoverBg = isGet ? 'group-hover:bg-blue-600' : 'group-hover:bg-indigo-600';

    return (
      <div className="min-h-screen bg-slate-100 flex flex-col items-center justify-center p-4">
        <div className="bg-white p-8 rounded-[2rem] shadow-2xl w-full max-w-md border border-slate-200 animate-in fade-in zoom-in duration-500 relative">
          <div className="text-center mb-10">
            <div className={`w-20 h-20 ${colorBg} rounded-2xl flex items-center justify-center text-white mx-auto mb-4 shadow-xl`}>
              <ModIcon size={40} />
            </div>
            <h1 className="text-3xl font-black text-slate-800 tracking-tight">Inicio de Sesión</h1>
            <p className="text-slate-500 font-medium">Accediendo a: {isGet ? 'Sistema GET' : 'Gestión FST-14'}</p>
          </div>
          
          <div className="space-y-4 mb-8">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest text-center mb-2">Seleccione su perfil de acceso</p>
            {usuarios.length > 0 ? usuarios.map(u => (
              <button 
                key={u.username} 
                onClick={() => { 
                  setCurrentUser(u); 
                  setCurrentScreen('dashboard'); 
                  if (activeModule === 'FST14') {
                    setFst14Tab(u.rol === 'Administrador' ? 'inbox' : 'form');
                  }
                }}
                className={`w-full p-4 rounded-2xl font-bold flex items-center justify-between border-2 border-slate-50 bg-slate-50 ${colorHover} hover:bg-white transition-all group shadow-sm hover:shadow-md`}
              >
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-xl bg-white flex items-center justify-center ${colorHoverBg} group-hover:text-white transition-all shadow-inner text-slate-400`}>
                    {u.rol === 'Administrador' ? <ShieldCheck size={20} /> : <User size={20} />}
                  </div>
                  <span className="text-slate-700 font-black">{safeStr(u.username)}</span>
                </div>
                <span className="text-[9px] uppercase font-black text-slate-400 bg-white px-2 py-1 rounded-lg border border-slate-100">{safeStr(u.rol)}</span>
              </button>
            )) : <p className="text-center text-slate-400 text-sm">Cargando usuarios...</p>}
          </div>

          <div className="border-t border-slate-200 pt-6 mt-6">
            <button 
              onClick={() => setActiveModule('none')}
              className="w-full bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100 py-4 rounded-2xl font-black text-xs uppercase tracking-widest transition-all flex justify-center items-center gap-2"
            >
              <ArrowLeft size={18} /> Volver al Portal
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 3. MÓDULO FST-14 INTERNO (BANDEJA DE ENTRADA Y FORMULARIO)
  if (activeModule === 'FST14') {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
        <header className="h-20 bg-white border-b flex items-center justify-between px-6 lg:px-10 shrink-0 shadow-sm z-10">
          <div className="flex items-center gap-4">
             <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg">
               <UserPlus size={20} />
             </div>
             <div>
               <h1 className="text-xl font-black text-slate-800 tracking-tighter leading-none">Módulo FST-14</h1>
               <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Gestión de Usuarios</p>
             </div>
          </div>
          <div className="flex items-center gap-4">
            {currentUser?.rol === 'Administrador' && (
              <div className="flex bg-slate-100 rounded-xl p-1">
                 <button onClick={() => setFst14Tab('inbox')} className={`px-4 py-2 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${fst14Tab === 'inbox' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:bg-slate-200'}`}>Bandeja</button>
                 <button onClick={() => setFst14Tab('form')} className={`px-4 py-2 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${fst14Tab === 'form' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:bg-slate-200'}`}>Nueva</button>
              </div>
            )}
            <div className="h-8 w-px bg-slate-200"></div>
            <button 
              onClick={() => setActiveModule('none')} 
              className="text-sm font-black uppercase tracking-widest text-slate-500 hover:text-indigo-600 transition-colors flex items-center gap-2 bg-slate-100 hover:bg-indigo-50 px-4 py-2.5 rounded-xl border border-slate-200"
            >
              <LayoutDashboard size={16} /> Volver al Portal
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6 lg:p-10 scrollbar-thin">
          <div className="max-w-5xl mx-auto space-y-8 animate-in slide-in-from-bottom-4 duration-500">
            {mensajeExito && (
              <div className="bg-emerald-50 border-2 border-emerald-100 text-emerald-700 p-4 rounded-2xl flex items-center gap-3 font-bold shadow-sm">
                <CheckCircle2 className="text-emerald-500" /> {mensajeExito}
              </div>
            )}

            {fst14Tab === 'inbox' && (
              <div className="bg-white rounded-[2.5rem] border border-slate-200 shadow-2xl flex flex-col p-8 overflow-hidden relative">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 border-b pb-6 gap-4">
                  <div>
                    <h3 className="text-2xl font-black text-slate-800 tracking-tighter flex items-center gap-3"><Inbox className="text-indigo-500"/> Solicitudes Recibidas</h3>
                    <p className="text-slate-500 text-sm mt-1">Bandeja de entrada general para gestión de usuarios FST-14.</p>
                  </div>
                </div>

                <div className="overflow-x-auto border border-slate-200 rounded-2xl scrollbar-thin">
                  <table className="w-full text-left min-w-[800px]">
                    <thead className="bg-slate-50 border-b border-slate-200">
                      <tr>
                        <th className="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Fecha / Estado</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Solicitante</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Acción</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">N° Usuarios</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest text-right">Detalles</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {fst14Requests.length > 0 ? fst14Requests.map(req => (
                        <tr key={req.id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-6 py-4">
                             <div className="font-black text-slate-800">{safeStr(req.fecha)}</div>
                             <span className="text-[10px] font-bold bg-amber-100 text-amber-700 px-2 py-0.5 rounded uppercase mt-1 inline-block">{safeStr(req.estadoSolicitud)}</span>
                          </td>
                          <td className="px-6 py-4">
                            <p className="font-bold text-sm text-slate-700">{safeStr(req.responsable)}</p>
                            <p className="text-xs text-slate-500">{safeStr(req.proceso)} - {safeStr(req.cargo)}</p>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider ${req.tipoAccion === 'CREACIÓN' ? 'bg-emerald-100 text-emerald-700' : req.tipoAccion === 'MODIFICACIÓN' ? 'bg-blue-100 text-blue-700' : 'bg-rose-100 text-rose-700'}`}>
                              {safeStr(req.tipoAccion)}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2 text-slate-600 font-bold">
                               <User size={16}/> {req.usuarios?.length || 0}
                            </div>
                          </td>
                          <td className="px-6 py-4 text-right">
                             <button onClick={() => setViewingFst14(req)} className="bg-white border border-slate-200 text-indigo-600 px-4 py-2 rounded-xl text-xs font-bold hover:bg-indigo-50 hover:border-indigo-200 transition-all flex items-center gap-2 ml-auto shadow-sm">
                               <Eye size={16}/> Ver Formulario
                             </button>
                          </td>
                        </tr>
                      )) : (
                        <tr>
                          <td colSpan="5" className="px-6 py-16 text-center text-slate-400">
                             <Inbox size={40} className="mx-auto mb-3 opacity-50"/>
                             <p className="font-bold text-lg text-slate-500">Bandeja Vacía</p>
                             <p className="text-sm">No se han recibido solicitudes FST-14.</p>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {fst14Tab === 'form' && renderFST14Form()}
          </div>
        </main>
        
        {/* MODAL VER SOLICITUD FST-14 */}
        {viewingFst14 && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
            <div className="bg-white w-full max-w-4xl rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col max-h-[95vh]">
              <div className="bg-indigo-600 p-6 flex justify-between items-center text-white shrink-0">
                <div className="flex items-center gap-3">
                  <ClipboardList size={28}/>
                  <h3 className="text-2xl font-black tracking-tighter">Detalle Solicitud FST-14</h3>
                </div>
                <button onClick={() => setViewingFst14(null)} className="bg-white/10 hover:bg-white/20 p-2 rounded-xl transition-all"><X size={24} /></button>
              </div>
              
              <div className="flex-1 overflow-y-auto p-8 md:p-10 scrollbar-thin bg-slate-50">
                 <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm space-y-8">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b pb-6">
                      <div>
                        <h4 className="font-black text-slate-800 text-xl">{safeStr(viewingFst14.tipoAccion)} DE USUARIOS</h4>
                        <p className="text-slate-500 text-sm mt-1">Radicado el: {new Date(viewingFst14.timestamp).toLocaleString()}</p>
                      </div>
                      <span className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wider ${viewingFst14.tipoAccion === 'CREACIÓN' ? 'bg-emerald-100 text-emerald-700' : viewingFst14.tipoAccion === 'MODIFICACIÓN' ? 'bg-blue-100 text-blue-700' : 'bg-rose-100 text-rose-700'}`}>
                        {safeStr(viewingFst14.tipoAccion)}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Fecha Doc.</p>
                        <p className="font-bold text-slate-800">{safeStr(viewingFst14.fecha)}</p>
                      </div>
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Proceso</p>
                        <p className="font-bold text-slate-800 truncate">{safeStr(viewingFst14.proceso)}</p>
                      </div>
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Solicitante</p>
                        <p className="font-bold text-slate-800 truncate">{safeStr(viewingFst14.responsable)}</p>
                      </div>
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Cargo</p>
                        <p className="font-bold text-slate-800 truncate">{safeStr(viewingFst14.cargo)}</p>
                      </div>
                    </div>

                    <div>
                      <h5 className="font-black text-sm text-slate-800 mb-3 border-b border-slate-100 pb-2">Usuarios Afectados</h5>
                      <div className="overflow-x-auto border border-slate-200 rounded-xl">
                        <table className="w-full text-left text-sm">
                          <thead className="bg-slate-50 border-b border-slate-200">
                            <tr>
                              <th className="px-4 py-3 font-bold text-slate-600">ID / CC</th>
                              <th className="px-4 py-3 font-bold text-slate-600">Nombre</th>
                              <th className="px-4 py-3 font-bold text-slate-600">Software</th>
                              <th className="px-4 py-3 font-bold text-slate-600">Perfil</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {viewingFst14.usuarios?.map((u, i) => (
                              <tr key={i}>
                                <td className="px-4 py-3">{safeStr(u.identificacion)}</td>
                                <td className="px-4 py-3">{safeStr(u.nombre)}</td>
                                <td className="px-4 py-3">{safeStr(u.software)}</td>
                                <td className="px-4 py-3">{safeStr(u.perfil)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {viewingFst14.observaciones && (
                      <div className="bg-amber-50 p-4 rounded-xl border border-amber-100">
                        <p className="text-[10px] font-black text-amber-600 uppercase tracking-widest mb-1">Observaciones / Detalles</p>
                        <p className="text-sm font-medium text-slate-700">{safeStr(viewingFst14.observaciones)}</p>
                      </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-100">
                      <div>
                         <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Firma del Solicitante</p>
                         <div className="h-[120px] bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-center p-2">
                           {viewingFst14.firmaSolicitante ? (
                             <img src={viewingFst14.firmaSolicitante} alt="Firma" className="max-h-full object-contain" />
                           ) : (
                             <span className="text-slate-400 text-sm font-medium italic">Sin firma digital</span>
                           )}
                         </div>
                      </div>
                      <div>
                         <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Canal de Ingreso</p>
                         <div className="h-[120px] bg-slate-50 rounded-xl border border-slate-200 flex flex-col items-center justify-center p-4 text-center">
                            <p className="text-sm font-bold text-slate-700 mb-1">Generado por:</p>
                            <p className="text-xs font-mono bg-white px-3 py-1 rounded border shadow-sm">{safeStr(viewingFst14.creadoPor)}</p>
                         </div>
                      </div>
                    </div>
                 </div>
              </div>
            </div>
          </div>
        )}

        {/* MODAL CONFIGURACIÓN FORMATO FST-14 */}
        {mostrarModalFst14Config && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
            <div className="bg-white w-full max-w-sm rounded-[2rem] shadow-2xl p-8">
              <h3 className="text-2xl font-black text-slate-800 mb-2">Configurar Formato</h3>
              <p className="text-xs text-slate-500 font-medium mb-6">Ajusta los datos del documento ISO 9001 para la solicitud de usuarios.</p>
              <form onSubmit={handleActualizarFst14Config} className="space-y-4">
                <div>
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Código del Formato</label>
                  <input name="formato" defaultValue={fst14Config.formato} required className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-indigo-400 text-slate-700" />
                </div>
                <div>
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Versión</label>
                  <input name="version" defaultValue={fst14Config.version} required className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-indigo-400 text-slate-700" />
                </div>
                <div>
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Fecha de Aprobación</label>
                  <input type="text" name="fecha" defaultValue={fst14Config.fecha} required placeholder="Ej: 16/08/2025" className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-indigo-400 text-slate-700" />
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button type="button" onClick={() => setMostrarModalFst14Config(false)} className="flex-1 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200">Cancelar</button>
                  <button type="submit" className="flex-1 py-3 bg-indigo-600 text-white font-bold rounded-xl shadow-lg hover:bg-indigo-700 active:scale-95">Guardar</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    );
  }

  // 5. MÓDULO SISTEMA GET (Principal)
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      {/* SIDEBAR GET */}
      <div 
        onMouseEnter={() => setSidebarColapsado(false)}
        onMouseLeave={() => setSidebarColapsado(true)}
        className={`fixed inset-y-0 left-0 z-50 bg-white border-r border-slate-200 flex flex-col transition-all duration-300 ease-in-out lg:relative lg:translate-x-0 ${menuAbierto ? 'translate-x-0' : '-translate-x-full'} ${sidebarColapsado ? 'w-20' : 'w-80'}`}
      >
        <div className="h-24 border-b flex items-center justify-center px-4 overflow-hidden shrink-0">
          <div className={`flex items-center gap-3 w-full ${sidebarColapsado ? 'justify-center' : 'justify-start px-2'} transition-all`}>
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg shrink-0">
              <Monitor size={20} />
            </div>
            {!sidebarColapsado && (
              <span className="text-xl font-black text-slate-800 leading-none tracking-tighter whitespace-nowrap animate-in fade-in duration-300">SISTEMA<br/>GET</span>
            )}
          </div>
          <button onClick={() => setMenuAbierto(false)} className="lg:hidden text-slate-400 absolute right-4"><X /></button>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto overflow-x-hidden scrollbar-thin">
          {[
            { id: 'dashboard', label: 'Inicio', icon: <LayoutDashboard size={20} /> },
            { id: 'identificar', label: 'Identificación de Equipos Tecnológicos', icon: <FileSearch size={20} /> },
            { id: 'seguimiento', label: 'Seguimiento de Equipos Tecnológicos', icon: <BarChart3 size={20} /> },
            { id: 'reportes', label: 'Reportes y Estadísticas', icon: <FileText size={20} /> },
            { id: 'historial', label: 'Historial de Cambios', icon: <History size={20} /> }
          ].map(item => (
            <button 
              key={item.id} 
              title={sidebarColapsado ? item.label : ""}
              onClick={() => { setCurrentScreen(item.id); setMenuAbierto(false); setSidebarColapsado(true); }}
              className={`w-full flex items-center ${sidebarColapsado ? 'justify-center px-0' : 'gap-4 px-4'} py-4 rounded-2xl transition-all whitespace-nowrap ${currentScreen === item.id ? 'bg-blue-600 text-white shadow-xl shadow-blue-100' : 'text-slate-500 hover:bg-slate-100'}`}
            >
              <div className="shrink-0">{item.icon}</div>
              {!sidebarColapsado && <span className="font-bold text-sm truncate">{item.label}</span>}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t shrink-0 overflow-hidden">
          {currentUser?.rol === 'Administrador' && (
            <button 
              title={sidebarColapsado ? "Configuración" : ""}
              onClick={() => { setCurrentScreen('configuracion'); setMenuAbierto(false); setSidebarColapsado(true); }}
              className={`w-full flex items-center ${sidebarColapsado ? 'justify-center px-0' : 'gap-4 px-4'} py-4 mb-2 rounded-2xl transition-all text-slate-500 hover:bg-slate-100 whitespace-nowrap`}
            >
              <div className="shrink-0"><Settings size={20} /></div>
              {!sidebarColapsado && <span className="font-bold text-sm truncate">Configuración</span>}
            </button>
          )}
          <button 
            title={sidebarColapsado ? "Volver al Portal" : ""}
            onClick={() => { setActiveModule('none'); setSidebarColapsado(true); }}
            className={`w-full flex items-center ${sidebarColapsado ? 'justify-center px-0' : 'gap-3 px-4'} py-4 rounded-2xl font-black text-xs uppercase tracking-widest bg-slate-100 text-slate-500 hover:bg-slate-200 transition-all whitespace-nowrap`}
          >
            <div className="shrink-0"><Grid size={18} /></div>
            {!sidebarColapsado && <span>Volver al Portal</span>}
          </button>
        </div>
      </div>

      {/* CONTENIDO PRINCIPAL DEL SISTEMA GET */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="h-24 bg-white border-b flex items-center justify-between px-6 lg:px-10 shrink-0">
          <button onClick={() => setMenuAbierto(true)} className="lg:hidden p-2 bg-slate-50 rounded-xl text-slate-500"><Menu /></button>
          
          <h2 className="text-xl font-black text-slate-800 lg:hidden">Sistema GET</h2>
          
          <div className="flex items-center gap-4 ml-auto">
             <div className="text-right hidden sm:block">
               <p className="text-sm font-black text-slate-800 uppercase leading-none">{safeStr(currentUser?.username)}</p>
               <p className="text-[10px] font-bold text-blue-600 uppercase mt-1 tracking-widest">{safeStr(currentUser?.rol)}</p>
             </div>
             <div className="w-12 h-12 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400 shadow-sm">
                <User size={24} />
             </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6 lg:p-10 scrollbar-thin">
          <div className="max-w-[1600px] w-full mx-auto">
            {mensajeExito && (
              <div className="bg-emerald-50 border-2 border-emerald-100 text-emerald-700 p-4 rounded-2xl flex items-center gap-3 mb-8 animate-in slide-in-from-top-4 duration-300 font-bold shadow-sm">
                <CheckCircle2 className="text-emerald-500" /> {mensajeExito}
              </div>
            )}

            {currentScreen === 'dashboard' && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div>
                    <h1 className="text-4xl font-black text-slate-800 tracking-tighter">Bienvenido, {safeStr(currentUser?.username)}</h1>
                    <p className="text-slate-500 font-medium text-lg mt-1">Este es el estado actual de tu infraestructura tecnológica.</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-10">
                  <div className="bg-white p-6 rounded-[2rem] border shadow-sm flex flex-col gap-4 relative overflow-hidden group">
                    <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-50 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
                    <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center shadow-inner relative z-10"><Box size={24} /></div>
                    <div className="relative z-10">
                      <p className="text-3xl font-black text-slate-800 tracking-tighter">{equipos.length}</p>
                      <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Total de Equipos</p>
                    </div>
                  </div>
                  <div className="bg-white p-6 rounded-[2rem] border shadow-sm flex flex-col gap-4 relative overflow-hidden group">
                    <div className="absolute -right-4 -top-4 w-24 h-24 bg-emerald-50 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
                    <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center shadow-inner relative z-10"><CheckCircle2 size={24} /></div>
                    <div className="relative z-10">
                      <div className="flex items-end gap-2">
                        <p className="text-3xl font-black text-slate-800 tracking-tighter">{equipos.filter(e => e.estado === 'Funcionando').length}</p>
                        <p className="text-sm font-bold text-emerald-500 mb-1">{equipos.length > 0 ? Math.round((equipos.filter(e => e.estado === 'Funcionando').length / equipos.length) * 100) : 0}%</p>
                      </div>
                      <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">En Funcionamiento</p>
                    </div>
                  </div>
                  <div className="bg-white p-6 rounded-[2rem] border shadow-sm flex flex-col gap-4 relative overflow-hidden group">
                    <div className="absolute -right-4 -top-4 w-24 h-24 bg-amber-50 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
                    <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-2xl flex items-center justify-center shadow-inner relative z-10"><Settings size={24} /></div>
                    <div className="relative z-10">
                      <p className="text-3xl font-black text-slate-800 tracking-tighter">{equipos.filter(e => e.estado === 'En Reparación').length}</p>
                      <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">En Reparación</p>
                    </div>
                  </div>
                  <div className="bg-white p-6 rounded-[2rem] border shadow-sm flex flex-col gap-4 relative overflow-hidden group">
                    <div className="absolute -right-4 -top-4 w-24 h-24 bg-rose-50 rounded-full group-hover:scale-150 transition-transform duration-500"></div>
                    <div className="w-12 h-12 bg-rose-100 text-rose-600 rounded-2xl flex items-center justify-center shadow-inner relative z-10"><AlertCircle size={24} /></div>
                    <div className="relative z-10">
                      <p className="text-3xl font-black text-slate-800 tracking-tighter">{equipos.filter(e => e.novedad && e.novedad !== 'Sin novedades').length}</p>
                      <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">Alertas Técnicas</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {currentScreen === 'identificar' && (
              <div className="bg-white p-8 rounded-[2rem] border shadow-sm animate-in slide-in-from-right-4 duration-500">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10">
                  <div>
                    <h2 className="text-3xl font-black text-slate-800 tracking-tighter">Identificación de Equipos Tecnológicos</h2>
                    <p className="text-slate-500 font-medium">Gestiona y consulta las fichas técnicas de tus activos.</p>
                  </div>
                  {(currentUser?.canCreate || currentUser?.rol === 'Administrador') && (
                    <button onClick={() => {
                        setTipoRegistro('Computadores');
                        setMostrarFormulario(true);
                      }} className="flex items-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-2xl font-black text-sm uppercase tracking-widest shadow-xl shadow-blue-200 hover:bg-blue-700 transition-all active:scale-95">
                      <Plus size={20} /> Agregar Registro
                    </button>
                  )}
                </div>

                {/* FILTROS BUSQUEDA */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8 bg-slate-50 p-6 rounded-3xl border border-slate-100">
                  <div className="relative group md:col-span-1">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-600 transition-colors" size={18} />
                    <input type="text" placeholder="Nombre o Código..." value={filtroIdentificar} onChange={e => setFiltroIdentificar(e.target.value)} className="w-full pl-12 pr-4 py-3 rounded-2xl border-none ring-2 ring-slate-100 focus:ring-blue-400 outline-none transition-all font-medium" />
                  </div>
                  <select value={filtroIdentificarTipo} onChange={e => setFiltroIdentificarTipo(e.target.value)} className="py-3 px-4 rounded-2xl bg-white ring-2 ring-slate-100 outline-none focus:ring-blue-400 font-bold text-slate-700">
                    <option value="Todos">Todos los tipos</option>
                    {TIPOS_EQUIPO.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                  <select value={filtroIdentificarEstado} onChange={e => setFiltroIdentificarEstado(e.target.value)} className="py-3 px-4 rounded-2xl bg-white ring-2 ring-slate-100 outline-none focus:ring-blue-400 font-bold text-slate-700">
                    <option value="Todos">Todos los estados</option>
                    <option value="Funcionando">Funcionando</option>
                    <option value="Activo">Activo</option>
                    <option value="En Reparación">En Reparación</option>
                    <option value="Inactivo">Inactivo</option>
                    <option value="De Baja">De Baja</option>
                  </select>
                  <input type="text" placeholder="Ubicación..." value={filtroIdentificarUbicacion} onChange={e => setFiltroIdentificarUbicacion(e.target.value)} className="py-3 px-4 rounded-2xl bg-white ring-2 ring-slate-100 outline-none focus:ring-blue-400 font-medium" />
                </div>

                <div className="overflow-auto max-h-[65vh] border rounded-3xl pb-2 scrollbar-thin relative">
                  <table className="w-full text-left min-w-[1000px]">
                    <thead className="bg-slate-50 sticky top-0 z-10 outline outline-1 outline-slate-200 shadow-sm">
                      <tr>
                        <th className="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest w-1/4 bg-slate-50">Dispositivo</th>
                        <th className="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest w-1/3 bg-slate-50">Detalles</th>
                        <th className="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest bg-slate-50">Ubicación</th>
                        <th className="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest text-center bg-slate-50">Estado</th>
                        <th className="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest text-right bg-slate-50">Acciones</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {filteredEquipos.map(eq => (
                        <tr key={eq.id} className="hover:bg-blue-50/30 transition-colors group">
                          <td className="px-6 py-5">
                            <div className="flex items-start gap-4">
                              <div className="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center text-slate-400 border shadow-inner overflow-hidden shrink-0">
                                {eq.foto ? <img src={safeStr(eq.foto)} className="w-full h-full object-cover" alt="foto" /> : (ICONS_TIPO[eq.tipo] || <Box size={24} />)}
                              </div>
                              <div className="min-w-0 flex-1">
                                <p className="font-black text-slate-800 leading-tight whitespace-normal break-words">{safeStr(eq.nombre)}</p>
                                <p className="text-[10px] font-black text-blue-600 uppercase tracking-widest mt-1">{safeStr(eq.codigo)}</p>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-5 min-w-[250px]">
                            <p className="text-xs font-bold text-slate-600 whitespace-normal break-words leading-relaxed">{safeStr(eq.descripcion)}</p>
                            <p className="text-[10px] text-slate-400 mt-2 font-mono bg-slate-50 inline-block px-2 py-1 rounded">S/N: {safeStr(eq.serie)}</p>
                          </td>
                          <td className="px-6 py-5 whitespace-normal">
                            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase break-words">
                              <div className="w-2 h-2 rounded-full bg-blue-500 shrink-0"></div> 
                              <span>{safeStr(eq.ubicacion)}</span>
                            </div>
                          </td>
                          <td className="px-6 py-5 text-center whitespace-nowrap">
                            <span className={`px-4 py-1.5 rounded-xl text-[10px] font-black border uppercase tracking-wider ${getEstadoClasses(eq.estado)}`}>
                              {safeStr(eq.estado)}
                            </span>
                          </td>
                          <td className="px-6 py-5 text-right space-x-2 whitespace-nowrap">
                             {(currentUser?.canEdit || currentUser?.rol === 'Administrador') && (
                               <button onClick={() => setEquipoEditando(eq)} className="p-3 bg-blue-50 text-blue-600 rounded-xl hover:bg-blue-600 hover:text-white transition-all shadow-sm"><Settings size={18} /></button>
                             )}
                             {(currentUser?.canDelete || currentUser?.rol === 'Administrador') && (
                               <button onClick={() => setEquipoAEliminar(eq)} className="p-3 bg-rose-50 text-rose-600 rounded-xl hover:bg-rose-600 hover:text-white transition-all shadow-sm"><X size={18} /></button>
                             )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {currentScreen === 'seguimiento' && (
              <div className="space-y-8 animate-in slide-in-from-right-4 duration-500">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                   <div>
                     <h2 className="text-3xl font-black text-slate-800 tracking-tighter flex items-center gap-3">
                       Seguimiento de Equipos Tecnológicos
                     </h2>
                     <p className="text-sm text-slate-500 font-medium mt-1">Registra el estado actual de los equipos, averías y mantenimientos.</p>
                   </div>
                </div>

                <div className="bg-white rounded-3xl border shadow-sm overflow-hidden flex flex-col">
                   {/* FILTROS SEGUIMIENTO */}
                   <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 bg-indigo-50/50 p-6 border-b border-indigo-100/50">
                     <div>
                        <label className="block text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">Búsqueda Libre</label>
                        <div className="relative">
                          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                          <input type="text" placeholder="Buscar nombre o código..." value={busqueda} onChange={e => setBusqueda(e.target.value)} className="w-full pl-9 pr-4 py-3 rounded-xl border border-white focus:border-indigo-400 outline-none shadow-sm text-sm" />
                        </div>
                     </div>
                     <div>
                        <label className="block text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">Ubicación</label>
                        <input type="text" placeholder="Filtrar ubicación..." value={filtroUbicacionSeguimiento} onChange={e => setFiltroUbicacionSeguimiento(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-white focus:border-indigo-400 outline-none shadow-sm text-sm" />
                     </div>
                     <div>
                        <label className="block text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">Tipo de Equipo</label>
                        <select value={filtroTipo} onChange={e => setFiltroTipo(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-white focus:border-indigo-400 outline-none shadow-sm text-sm font-bold text-slate-700">
                          <option value="Todos">Todos los tipos</option>
                          {TIPOS_EQUIPO.map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                     </div>
                     <div>
                        <label className="block text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">Estado Operativo</label>
                        <select value={filtroEstado} onChange={e => setFiltroEstado(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-white focus:border-indigo-400 outline-none shadow-sm text-sm font-bold text-slate-700">
                          <option value="Todos">Todos los estados</option>
                          <option value="Funcionando">Funcionando</option>
                          <option value="Activo">Activo</option>
                          <option value="En Reparación">En Reparación</option>
                          <option value="Inactivo">Inactivo</option>
                          <option value="De Baja">De Baja</option>
                        </select>
                     </div>
                   </div>

                   {/* TABLA DE SEGUIMIENTO */}
                   <div className="overflow-auto max-h-[65vh] w-full pb-2 scrollbar-thin relative">
                     <table className="min-w-[1200px] w-full text-left divide-y divide-slate-100 text-sm">
                       <thead className="bg-slate-50 sticky top-0 z-10 outline outline-1 outline-slate-200 shadow-sm">
                         <tr>
                           <th className="px-6 py-4 font-black text-slate-500 uppercase tracking-widest text-[10px] w-32 bg-slate-50">Código</th>
                           <th className="px-6 py-4 font-black text-slate-500 uppercase tracking-widest text-[10px] w-1/4 bg-slate-50">Equipo</th>
                           <th className="px-6 py-4 font-black text-slate-500 uppercase tracking-widest text-[10px] w-1/5 bg-slate-50">Responsable / Ubic.</th>
                           <th className="px-6 py-4 font-black text-slate-500 uppercase tracking-widest text-[10px] bg-slate-50">Estado Actual</th>
                           <th className="px-6 py-4 font-black text-slate-500 uppercase tracking-widest text-[10px] bg-slate-50">Fecha de Seguimiento</th>
                           <th className="px-6 py-4 font-black text-slate-500 uppercase tracking-widest text-[10px] w-1/4 bg-slate-50">Novedades / Averías</th>
                           <th className="px-6 py-4 font-black text-slate-500 uppercase tracking-widest text-[10px] text-right bg-slate-50">Seguimiento</th>
                         </tr>
                       </thead>
                       <tbody className="bg-white divide-y divide-slate-50">
                         {equipos.filter(eq => {
                           const eqNombre = eq.nombre ? String(eq.nombre).toLowerCase() : '';
                           const eqCodigo = eq.codigo ? String(eq.codigo).toLowerCase() : '';
                           const eqUbicacion = eq.ubicacion ? String(eq.ubicacion).toLowerCase() : '';
                           
                           return (filtroTipo === 'Todos' || eq.tipo === filtroTipo) && 
                                  (filtroEstado === 'Todos' || eq.estado === filtroEstado) && 
                                  (eqNombre.includes(busqueda.toLowerCase()) || eqCodigo.includes(busqueda.toLowerCase())) && 
                                  (!filtroUbicacionSeguimiento || eqUbicacion.includes(filtroUbicacionSeguimiento.toLowerCase()))
                         }).length > 0 ? (
                           equipos.filter(eq => {
                             const eqNombre = eq.nombre ? String(eq.nombre).toLowerCase() : '';
                             const eqCodigo = eq.codigo ? String(eq.codigo).toLowerCase() : '';
                             const eqUbicacion = eq.ubicacion ? String(eq.ubicacion).toLowerCase() : '';
                             
                             return (filtroTipo === 'Todos' || eq.tipo === filtroTipo) && 
                                    (filtroEstado === 'Todos' || eq.estado === filtroEstado) && 
                                    (eqNombre.includes(busqueda.toLowerCase()) || eqCodigo.includes(busqueda.toLowerCase())) && 
                                    (!filtroUbicacionSeguimiento || eqUbicacion.includes(filtroUbicacionSeguimiento.toLowerCase()))
                           }).map(equipo => (
                             <tr key={equipo.id} className="hover:bg-indigo-50/30 transition-all group">
                               <td className="px-6 py-5 whitespace-nowrap">
                                 <div className="font-black text-slate-800 text-sm tracking-tight">{safeStr(equipo.codigo)}</div>
                               </td>
                               <td className="px-6 py-5 min-w-[200px]">
                                 <div className="font-bold text-slate-800 text-sm whitespace-normal break-words">{safeStr(equipo.nombre)}</div>
                                 <div className="text-[10px] text-indigo-600 font-black tracking-widest uppercase mt-1">{safeStr(equipo.tipo)}</div>
                               </td>
                               <td className="px-6 py-5 text-xs text-slate-600 min-w-[200px] whitespace-normal break-words">
                                 {equipo.responsable && equipo.responsable !== 'N/A' ? (
                                   <div className="font-bold flex items-start gap-2"><User size={14} className="text-slate-400 shrink-0 mt-0.5"/> <span>{safeStr(equipo.responsable)}</span></div>
                                 ) : (
                                   <div className="flex items-start gap-2 text-slate-500"><Wifi size={14} className="text-slate-400 shrink-0 mt-0.5"/> <span>{safeStr(equipo.ubicacion)}</span></div>
                                 )}
                               </td>
                               <td className="px-6 py-5 whitespace-nowrap">
                                 <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-black border uppercase tracking-wider ${getEstadoClasses(equipo.estado)}`}>
                                   {safeStr(equipo.estado)}
                                 </span>
                               </td>
                               <td className="px-6 py-5 whitespace-nowrap text-xs">
                                 <div className="font-bold text-slate-700">{safeStr(equipo.ultimaInspeccion || 'Sin registro previo')}</div>
                               </td>
                               <td className="px-6 py-5 text-xs text-slate-600 min-w-[250px]">
                                 {equipo.novedad && equipo.novedad !== 'Sin novedades' ? (
                                   <span className="text-amber-700 font-bold bg-amber-50 px-3 py-2 rounded-xl border border-amber-200 block whitespace-normal break-words">{safeStr(equipo.novedad)}</span>
                                 ) : (
                                   <span className="text-slate-400 italic">Sin novedades</span>
                                 )}
                               </td>
                               <td className="px-6 py-5 whitespace-nowrap text-right">
                                 {(currentUser?.rol === 'Administrador' || currentUser?.canReview) ? (
                                   <button 
                                     className="flex items-center gap-2 px-4 py-2 rounded-xl transition-all font-bold text-xs shadow-sm border text-indigo-600 bg-white hover:bg-indigo-50 border-indigo-200 ml-auto"
                                     onClick={() => handleAbrirRevision(equipo)}
                                   >
                                     <Settings size={14} className="transition-transform duration-300" />
                                     Revisar
                                   </button>
                                 ) : (
                                   <span className="text-xs text-slate-400 italic">Sin permisos</span>
                                 )}
                               </td>
                             </tr>
                           ))
                         ) : (
                           <tr>
                             <td colSpan="7" className="px-6 py-16 text-center text-slate-500">
                               <div className="flex flex-col items-center justify-center">
                                 <FileSearch size={40} className="text-slate-300 mb-4" />
                                 <p className="font-black text-lg text-slate-700">No hay equipos</p>
                                 <p className="text-sm mt-1">Ajusta los filtros o realiza una búsqueda distinta.</p>
                               </div>
                             </td>
                           </tr>
                         )}
                       </tbody>
                     </table>
                   </div>
                </div>
              </div>
            )}

            {currentScreen === 'reportes' && (
              <div className="space-y-8 animate-in slide-in-from-right-4 duration-500">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8">
                  <div>
                    <h2 className="text-3xl font-black text-slate-800 tracking-tighter">Reportes y Estadísticas</h2>
                    <p className="text-slate-500 font-medium">Analíticas del inventario general.</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-white p-8 rounded-[2rem] border shadow-sm">
                    <h3 className="font-black text-slate-700 uppercase tracking-widest text-xs mb-6">Distribución por Estado</h3>
                    <div className="space-y-4">
                      {['Funcionando', 'Activo', 'En Reparación', 'Inactivo', 'De Baja'].map(estado => {
                        const count = equipos.filter(e => e.estado === estado).length;
                        if (count === 0 && equipos.length > 0) return null;
                        const percentage = equipos.length === 0 ? 0 : Math.round((count / equipos.length) * 100);
                        const colorClass = estado === 'Funcionando' || estado === 'Activo' ? 'bg-emerald-500' : estado === 'En Reparación' ? 'bg-amber-500' : estado === 'De Baja' ? 'bg-rose-500' : 'bg-slate-400';
                        return (
                          <div key={estado}>
                            <div className="flex justify-between text-xs font-bold text-slate-600 mb-2">
                              <span>{estado}</span>
                              <span>{count} ({percentage}%)</span>
                            </div>
                            <div className="w-full bg-slate-100 rounded-full h-3">
                              <div className={`${colorClass} h-3 rounded-full transition-all`} style={{ width: `${percentage}%` }}></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  
                  <div className="bg-white p-8 rounded-[2rem] border shadow-sm flex flex-col">
                    <h3 className="font-black text-slate-700 uppercase tracking-widest text-xs mb-6 flex items-center justify-between">
                      Alertas Recientes <span className="bg-rose-100 text-rose-700 px-2 py-1 rounded-md">{equipos.filter(e => e.novedad && e.novedad !== 'Sin novedades').length}</span>
                    </h3>
                    <div className="space-y-4 flex-1 overflow-y-auto max-h-64 pr-2 scrollbar-thin">
                      {equipos.filter(e => e.novedad && e.novedad !== 'Sin novedades').length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-slate-400 opacity-70">
                          <CheckCircle2 size={48} className="mb-2 text-emerald-400" />
                          <p className="text-sm font-bold">Sin alertas reportadas</p>
                        </div>
                      ) : (
                        equipos.filter(e => e.novedad && e.novedad !== 'Sin novedades').map(eq => (
                          <div key={eq.id} className="p-4 bg-rose-50 rounded-2xl border border-rose-100">
                            <p className="font-black text-rose-800 text-sm">{safeStr(eq.nombre)}</p>
                            <p className="text-xs text-rose-600 font-medium mt-1">{safeStr(eq.novedad)}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {currentScreen === 'historial' && (
              <div className="bg-white p-8 rounded-[2rem] border shadow-sm animate-in slide-in-from-right-4 duration-500">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8">
                  <div>
                    <h2 className="text-3xl font-black text-slate-800 tracking-tighter">Historial de Cambios</h2>
                    <p className="text-slate-500 font-medium">Registro de actividades y cambios en el sistema.</p>
                  </div>
                </div>
                <div className="overflow-auto max-h-[65vh] border rounded-3xl scrollbar-thin relative">
                  <table className="w-full text-left min-w-[1000px]">
                    <thead className="bg-slate-50 sticky top-0 z-10 outline outline-1 outline-slate-200 shadow-sm">
                      <tr>
                        <th className="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest bg-slate-50">Fecha</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest bg-slate-50">Usuario</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest bg-slate-50">Acción</th>
                        <th className="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest w-1/2 bg-slate-50">Detalles</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {historialLogs.map(log => (
                        <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-6 py-4 text-xs font-mono text-slate-500 whitespace-nowrap">
                            {new Date(log.timestamp).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-sm font-bold text-slate-700 whitespace-nowrap">
                            {safeStr(log.usuario)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider ${log.accion === 'Creación' ? 'bg-emerald-100 text-emerald-700' : log.accion === 'Edición' ? 'bg-blue-100 text-blue-700' : log.accion === 'Eliminación' ? 'bg-rose-100 text-rose-700' : 'bg-indigo-100 text-indigo-700'}`}>
                              {safeStr(log.accion)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-600 min-w-[300px]">
                            <p className="font-bold text-sm text-slate-800 mb-1 whitespace-normal break-words">{safeStr(log.equipoNombre)}</p>
                            <p className="opacity-80 leading-relaxed whitespace-normal break-words">{safeStr(log.detalles)}</p>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {currentScreen === 'configuracion' && currentUser?.rol === 'Administrador' && (
              <div className="space-y-8 animate-in slide-in-from-right-4 duration-500">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8">
                  <div>
                    <h2 className="text-3xl font-black text-slate-800 tracking-tighter">Configuración y Control (ISO 9001)</h2>
                    <p className="text-slate-500 font-medium">Gestión de calidad, versiones, usuarios y permisos del sistema GET.</p>
                  </div>
                </div>

                <div className="bg-indigo-50 p-6 rounded-[2rem] border border-indigo-100 flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-indigo-600 shadow-sm shrink-0 border border-indigo-100">
                      <FileText size={32} />
                    </div>
                    <div>
                      <h4 className="font-black text-xl text-indigo-900 tracking-tight">Control de Versiones del Documento</h4>
                      <p className="text-sm font-medium text-indigo-700 mt-1 flex items-center gap-2">
                        <span className="font-bold bg-indigo-200 px-2 py-0.5 rounded text-indigo-800">Versión {safeStr(versionInfo?.version)}</span> 
                        &bull; Actualizado: {safeStr(versionInfo?.fecha)}
                      </p>
                      <p className="text-xs text-indigo-600/80 mt-1 max-w-md truncate">Notas: {safeStr(versionInfo?.notas)}</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setMostrarModalVersion(true)}
                    className="w-full md:w-auto px-6 py-3 bg-indigo-600 text-white font-bold text-sm rounded-xl shadow-lg shadow-indigo-200 hover:bg-indigo-700 active:scale-95 transition-all whitespace-nowrap"
                  >
                    Actualizar Versión
                  </button>
                </div>

                <div className="bg-amber-50 p-6 rounded-[2rem] border border-amber-100 flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm mt-6">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-amber-600 shadow-sm shrink-0 border border-amber-100">
                      <Database size={32} />
                    </div>
                    <div>
                      <h4 className="font-black text-xl text-amber-900 tracking-tight">Datos de Prueba</h4>
                      <p className="text-sm font-medium text-amber-700 mt-1">Genera automáticamente un conjunto de equipos de demostración.</p>
                    </div>
                  </div>
                  <button 
                    onClick={generarDatosDePrueba}
                    className="w-full md:w-auto px-6 py-3 bg-amber-600 text-white font-bold text-sm rounded-xl shadow-lg shadow-amber-200 hover:bg-amber-700 active:scale-95 transition-all whitespace-nowrap"
                  >
                    Insertar Datos de Prueba
                  </button>
                </div>

                <h3 className="text-xl font-black text-slate-800 mt-8 mb-4 border-b pb-2">Gestión de Usuarios</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {usuarios.map(u => (
                    <div key={u.username} className="bg-white p-6 rounded-[2rem] border shadow-sm">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-black text-xl text-slate-800 flex items-center gap-2">
                          <User size={20} className="text-blue-500" /> {safeStr(u.username)}
                        </h4>
                        <span className="text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-lg bg-slate-100 text-slate-600 border border-slate-200">{safeStr(u.rol)}</span>
                      </div>
                      <div className="flex flex-wrap gap-2 mb-6">
                        {u.canCreate && <span className="text-[10px] bg-emerald-50 text-emerald-600 font-bold px-2 py-1 rounded">Crear</span>}
                        {u.canEdit && <span className="text-[10px] bg-blue-50 text-blue-600 font-bold px-2 py-1 rounded">Editar</span>}
                        {u.canDelete && <span className="text-[10px] bg-rose-50 text-rose-600 font-bold px-2 py-1 rounded">Eliminar</span>}
                        {u.canReview && <span className="text-[10px] bg-indigo-50 text-indigo-600 font-bold px-2 py-1 rounded">Revisar</span>}
                      </div>
                      <button 
                        onClick={() => setUsuarioEditando(u)}
                        disabled={u.username === 'admin'}
                        className="w-full py-3 bg-slate-50 text-slate-700 font-bold text-sm rounded-xl hover:bg-slate-100 disabled:opacity-50 transition-colors"
                      >
                        {u.username === 'admin' ? 'Protegido' : 'Editar Permisos'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        </main>
      </div>

      {/* MODALES ADICIONALES */}
      
      {/* MODAL EDICIÓN USUARIO */}
      {usuarioEditando && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-sm rounded-[2rem] shadow-2xl p-8">
            <h3 className="text-2xl font-black text-slate-800 mb-6">Editar Permisos</h3>
            <form onSubmit={handleActualizarPermisos} className="space-y-4">
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Rol del Usuario</label>
                <select name="rol" defaultValue={usuarioEditando.rol} className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold text-slate-700 outline-none">
                  <option value="Administrador">Administrador</option>
                  <option value="Auxiliar">Auxiliar</option>
                  <option value="Visitante">Visitante</option>
                </select>
              </div>
              <div className="space-y-2 p-4 bg-slate-50 rounded-xl border border-slate-100">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" name="canCreate" defaultChecked={usuarioEditando.canCreate} className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500" />
                  <span className="text-sm font-bold text-slate-600">Crear Equipos</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" name="canEdit" defaultChecked={usuarioEditando.canEdit} className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500" />
                  <span className="text-sm font-bold text-slate-600">Editar Equipos</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" name="canDelete" defaultChecked={usuarioEditando.canDelete} className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500" />
                  <span className="text-sm font-bold text-slate-600">Eliminar Equipos</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" name="canReview" defaultChecked={usuarioEditando.canReview} className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500" />
                  <span className="text-sm font-bold text-slate-600">Hacer Seguimientos</span>
                </label>
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setUsuarioEditando(null)} className="flex-1 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200">Cancelar</button>
                <button type="submit" className="flex-1 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-lg hover:bg-blue-700 active:scale-95">Guardar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL VERSIÓN ISO 9001 */}
      {mostrarModalVersion && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-sm rounded-[2rem] shadow-2xl p-8">
            <h3 className="text-2xl font-black text-slate-800 mb-2">Control de Cambios</h3>
            <p className="text-xs text-slate-500 font-medium mb-6">Actualiza la versión del sistema para el registro de calidad ISO 9001.</p>
            <form onSubmit={handleActualizarVersion} className="space-y-4">
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Nueva Versión</label>
                <input name="version" defaultValue={versionInfo?.version} placeholder="Ej: 1.1" required className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-indigo-400 text-slate-700" />
              </div>
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Fecha de Actualización</label>
                <input type="date" name="fecha" defaultValue={versionInfo?.fecha || new Date().toISOString().split('T')} required className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-indigo-400 text-slate-700" />
              </div>
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Notas / Descripción del Cambio</label>
                <textarea name="notas" rows="3" defaultValue={versionInfo?.notas} required placeholder="Describe brevemente los cambios realizados..." className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-medium outline-none focus:border-indigo-400 resize-none text-slate-700"></textarea>
              </div>
              
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setMostrarModalVersion(false)} className="flex-1 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200">Cancelar</button>
                <button type="submit" className="flex-1 py-3 bg-indigo-600 text-white font-bold rounded-xl shadow-lg hover:bg-indigo-700 active:scale-95">Actualizar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL REVISIÓN EQUIPO (SEGUIMIENTO MENSUAL) */}
      {equipoEnRevision && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-4xl rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col max-h-[95vh]">
            <div className="bg-indigo-600 p-8 flex justify-between items-center text-white shrink-0">
              <div>
                <h3 className="text-3xl font-black tracking-tighter">Seguimiento Mensual</h3>
                <p className="text-indigo-100 font-medium text-sm mt-1">Actualizando control para: <strong>{safeStr(equipoEnRevision.nombre)} ({safeStr(equipoEnRevision.codigo)})</strong></p>
              </div>
              <button onClick={() => setEquipoEnRevision(null)} className="bg-white/10 hover:bg-white/20 p-2 rounded-2xl transition-all"><X size={32} /></button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-10 scrollbar-thin">
              <form onSubmit={handleGuardarRevision} className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-slate-50 p-6 rounded-2xl border border-slate-100 shadow-sm">
                  <div>
                    <label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest block mb-2">Fecha de Seguimiento</label>
                    <input 
                      type="date" 
                      name="fechaRevision" 
                      defaultValue={new Date().toISOString().split('T')} 
                      className="w-full p-3 text-sm font-bold bg-white rounded-xl outline-none border border-slate-200 focus:border-indigo-400 text-slate-700" 
                      required
                    />
                  </div>
                  <div>
                    <label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest block mb-2">Estado Operativo Actual</label>
                    <select name="estado" defaultValue={equipoEnRevision.estado} className="w-full p-3 text-sm font-bold bg-white rounded-xl outline-none border border-slate-200 focus:border-indigo-400 text-slate-700">
                      <option value="Funcionando">Funcionando</option>
                      <option value="Activo">Activo</option>
                      <option value="En Reparación">En Reparación</option>
                      <option value="Inactivo">Inactivo</option>
                      <option value="De Baja">De Baja</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 bg-indigo-50/50 p-6 rounded-2xl border border-indigo-100">
                  {/* CHECKLIST HARDWARE */}
                  <div className="col-span-1 sm:col-span-2 bg-white p-5 rounded-2xl border border-indigo-100 shadow-sm">
                    <label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest block mb-4 border-b border-indigo-50 pb-2">Checklist Físico / Hardware ({safeStr(equipoEnRevision.tipo)})</label>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      {getChecklistItems(equipoEnRevision.tipo).hw.map(item => (
                        <div key={item}>
                          <label className="text-[10px] font-black text-slate-400 block mb-2 text-center uppercase truncate" title={item}>{item}</label>
                          <div 
                            onClick={() => setHwRevision(prev => ({ ...prev, [item]: prev[item] === ' ✔ ' ? ' ✖ ' : ' ✔ ' }))}
                            className={`cursor-pointer w-full p-3 text-xl font-black text-center rounded-xl border transition-all duration-200 select-none shadow-sm active:scale-95 ${hwRevision[item] === ' ✔ ' ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : 'bg-rose-50 text-rose-600 border-rose-200'}`}
                          >
                            {String(hwRevision[item] || ' ✔ ')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* CHECKLIST SOFTWARE */}
                  <div className="col-span-1 sm:col-span-2 bg-white p-5 rounded-2xl border border-indigo-100 shadow-sm">
                    <label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest block mb-4 border-b border-indigo-50 pb-2">Checklist Lógico / Software</label>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 items-end">
                      {getChecklistItems(equipoEnRevision.tipo).sw.map(item => {
                        if (item === 'SO') {
                          return (
                            <div className="col-span-2 sm:col-span-4 lg:col-span-2" key={item}>
                              <label className="text-[10px] font-black text-slate-400 block mb-2 uppercase">Sistema Operativo</label>
                              <div className="flex gap-2">
                                <select 
                                  value={swRevision.so} 
                                  onChange={e => setSwRevision(prev => ({...prev, so: e.target.value}))} 
                                  className="w-full p-3 text-sm font-bold bg-slate-50 rounded-xl border border-slate-200 focus:border-indigo-400 text-slate-700 outline-none"
                                >
                                  {['Tablet', 'Celulares'].includes(equipoEnRevision.tipo) ? (
                                    <><option value="Android">Android</option><option value="iOS">iOS</option><option value="Otro">Otro...</option></>
                                  ) : (
                                    <><option value="Windows 10">Windows 10</option><option value="Windows 11">Windows 11</option><option value="macOS">macOS</option><option value="Otro">Otro...</option></>
                                  )}
                                </select>
                                {swRevision.so === 'Otro' && (
                                  <input 
                                    type="text" 
                                    value={swRevision.soOtro} 
                                    onChange={e => setSwRevision(prev => ({...prev, soOtro: e.target.value}))} 
                                    className="w-full p-3 text-sm font-medium bg-white rounded-xl border border-slate-200 focus:border-indigo-400 outline-none" 
                                    placeholder="Especifique..." 
                                    required 
                                  />
                                )}
                              </div>
                            </div>
                          );
                        }
                        if (item === 'Configuración' && equipoEnRevision.tipo === 'Impresoras') {
                          return (
                            <div className="col-span-2 sm:col-span-4 lg:col-span-2" key={item}>
                              <label className="text-[10px] font-black text-slate-400 block mb-2 uppercase">Conexión de Impresora</label>
                              <select 
                                value={swRevision.configuracion || 'USB'} 
                                onChange={e => setSwRevision(prev => ({...prev, configuracion: e.target.value}))} 
                                className="w-full p-3 text-sm font-bold bg-slate-50 rounded-xl border border-slate-200 focus:border-indigo-400 text-slate-700 outline-none"
                              >
                                <option value="USB">USB (Local)</option>
                                <option value="RED">RED (Ethernet)</option>
                                <option value="WIFI">Wi-Fi (Inalámbrico)</option>
                              </select>
                            </div>
                          );
                        }
                        return (
                          <div key={item}>
                            <label className="text-[10px] font-black text-slate-400 block mb-2 text-center uppercase truncate" title={item}>{item}</label>
                            <div 
                              onClick={() => setSwRevision(prev => ({ ...prev, [item]: prev[item] === ' ✔ ' ? ' ✖ ' : ' ✔ ' }))}
                              className={`cursor-pointer w-full p-3 text-xl font-black text-center rounded-xl border transition-all duration-200 select-none shadow-sm active:scale-95 ${swRevision[item] === ' ✔ ' ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : 'bg-rose-50 text-rose-600 border-rose-200'}`}
                            >
                              {String(swRevision[item] || ' ✔ ')}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div>
                    <label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest block mb-2">¿Genera ODT?</label>
                    <select name="odt" defaultValue={equipoEnRevision.odt || 'No'} className="w-full p-3 text-sm font-bold bg-white rounded-xl border border-slate-200 focus:border-indigo-400 text-slate-700 outline-none">
                      <option value="No">No</option>
                      <option value="Sí">Sí</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest block mb-2">N° de Orden (ODT)</label>
                    <input name="numeroOdt" defaultValue={equipoEnRevision.numeroOdt || ''} placeholder="Ej: 40552" className="w-full p-3 text-sm font-bold bg-white rounded-xl border border-slate-200 focus:border-indigo-400 text-slate-700 outline-none" />
                  </div>
                </div>

                <div className="bg-amber-50/50 p-6 rounded-2xl border border-amber-200 shadow-sm">
                  <label className="text-[10px] font-black text-amber-600 uppercase tracking-widest block mb-2 flex items-center gap-2"><AlertTriangle size={14}/> Reporte de Novedades / Averías</label>
                  <textarea name="novedad" defaultValue={equipoEnRevision.novedad !== 'Sin novedades' ? equipoEnRevision.novedad : ''} rows="3" className="w-full bg-white border border-amber-200 p-4 text-sm font-medium rounded-xl outline-none resize-none focus:border-amber-400 transition-colors text-slate-700" placeholder="Detalla si el equipo presenta fallas, requiere mantenimiento, piezas, etc..."></textarea>
                </div>
                
                <div className="flex gap-4 pt-4 border-t border-slate-100">
                  <button type="button" onClick={()=>setEquipoEnRevision(null)} className="flex-1 py-4 bg-slate-100 text-slate-600 rounded-xl font-black text-xs uppercase tracking-widest border border-slate-200 hover:bg-slate-200 shadow-sm transition-all">Cancelar</button>
                  <button type="submit" className="flex-1 py-4 bg-indigo-600 text-white rounded-xl font-black text-xs uppercase tracking-widest shadow-xl shadow-indigo-200 hover:bg-indigo-700 active:scale-95 transition-all">Guardar Seguimiento</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* MODAL EDICIÓN DE EQUIPO */}
      {equipoEditando && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-lg rounded-[2rem] shadow-2xl p-8">
            <h3 className="text-2xl font-black text-slate-800 mb-6">Editar Equipo</h3>
            <form onSubmit={handleActualizarEquipo} className="space-y-4">
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Código / Placa</label>
                <input name="codigo" defaultValue={equipoEditando.codigo} required className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-blue-400" />
              </div>
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Nombre</label>
                <input name="nombre" defaultValue={equipoEditando.nombre} required className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-blue-400" />
              </div>
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Ubicación</label>
                <input name="ubicacion" defaultValue={equipoEditando.ubicacion} required className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-blue-400" />
              </div>
              <div>
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Responsable</label>
                <input name="responsable" defaultValue={equipoEditando.responsable} required className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-blue-400" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Estado</label>
                  <select name="estado" defaultValue={equipoEditando.estado} className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-blue-400">
                    <option value="Funcionando">Funcionando</option>
                    <option value="Activo">Activo</option>
                    <option value="En Reparación">En Reparación</option>
                    <option value="Inactivo">Inactivo</option>
                    <option value="De Baja">De Baja</option>
                  </select>
                </div>
                <div>
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">¿Tiene QR?</label>
                  <select name="tieneQR" defaultValue={equipoEditando.tieneQR} className="w-full p-3 rounded-xl border-2 border-slate-100 mt-1 font-bold outline-none focus:border-blue-400">
                    <option value="Sí">Sí</option>
                    <option value="No">No</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setEquipoEditando(null)} className="flex-1 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200">Cancelar</button>
                <button type="submit" className="flex-1 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-lg hover:bg-blue-700 active:scale-95">Actualizar</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL ELIMINAR EQUIPO */}
      {equipoAEliminar && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-sm rounded-[2rem] shadow-2xl p-8 text-center">
            <div className="w-20 h-20 bg-rose-50 text-rose-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <X size={40} />
            </div>
            <h3 className="text-2xl font-black text-slate-800 mb-2">¿Eliminar Equipo?</h3>
            <p className="text-slate-500 text-sm mb-6">Estás a punto de borrar permanentemente <strong>{safeStr(equipoAEliminar.nombre)}</strong>. Esta acción no se puede deshacer.</p>
            <div className="flex gap-3">
              <button onClick={() => setEquipoAEliminar(null)} className="flex-1 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200">Cancelar</button>
              <button onClick={handleEliminarEquipo} className="flex-1 py-3 bg-rose-600 text-white font-bold rounded-xl shadow-lg shadow-rose-200 hover:bg-rose-700 active:scale-95">Sí, Eliminar</button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL REGISTRO SUPER DETALLADO */}
      {mostrarFormulario && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-5xl rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col max-h-[95vh]">
            <div className="bg-blue-600 p-8 flex justify-between items-center text-white shrink-0">
              <div>
                <h3 className="text-3xl font-black tracking-tighter">Nuevo Equipo</h3>
                <p className="text-blue-100 font-medium text-sm mt-1">Completa los datos técnicos para el inventario.</p>
              </div>
              <button onClick={() => setMostrarFormulario(false)} className="bg-white/10 hover:bg-white/20 p-2 rounded-2xl transition-all"><X size={32} /></button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-10 scrollbar-thin">
              <form onSubmit={handleRegistrarEquipo} className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Código de Placa *</label>
                    <input name="codigo" required className="w-full p-4 rounded-2xl bg-slate-50 border-2 border-slate-50 focus:border-blue-400 outline-none font-bold text-lg transition-all" placeholder="Ej: INV-001" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Nombre del Dispositivo *</label>
                    <input name="nombre" required className="w-full p-4 rounded-2xl bg-slate-50 border-2 border-slate-50 focus:border-blue-400 outline-none font-bold text-lg transition-all" placeholder="Ej: Computador Contabilidad" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Categoría de Equipo</label>
                    <select name="tipo" value={tipoRegistro} onChange={e => setTipoRegistro(e.target.value)} className="w-full p-4 rounded-2xl bg-slate-50 border-2 border-slate-50 focus:border-blue-400 outline-none font-bold text-slate-700 cursor-pointer">
                      {TIPOS_EQUIPO.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Estado Inicial</label>
                    <select name="estado" className="w-full p-4 rounded-2xl bg-slate-50 border-2 border-slate-50 focus:border-blue-400 outline-none font-bold text-slate-700 cursor-pointer">
                      <option value="Funcionando">Funcionando</option>
                      <option value="Activo">Activo</option>
                      <option value="En Reparación">En Reparación</option>
                      <option value="Inactivo">Inactivo</option>
                      <option value="De Baja">De Baja</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">¿Etiquetado con QR?</label>
                    <select name="tieneQR" className="w-full p-4 rounded-2xl bg-slate-50 border-2 border-slate-50 focus:border-blue-400 outline-none font-bold text-slate-700 cursor-pointer">
                      <option value="Sí">Sí</option>
                      <option value="No">No</option>
                    </select>
                  </div>
                </div>

                {/* COMPUTADORES */}
                {tipoRegistro === 'Computadores' && (
                  <div className="p-6 bg-blue-50/50 rounded-3xl border border-blue-100 grid grid-cols-2 md:grid-cols-4 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-2 md:col-span-4 mb-2 border-b border-blue-100 pb-2"><h4 className="font-black text-blue-800 flex items-center gap-2"><Monitor size={18}/> Especificaciones Técnicas (PC)</h4></div>
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-blue-500 uppercase tracking-widest ml-1">Formato</label><select name="formatoComputador" value={formatoComputador} onChange={e=>setFormatoComputador(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-blue-100 outline-none focus:border-blue-400 font-bold text-slate-700"><option>Portátil</option><option>Torre</option><option>Todo en Uno</option></select></div>
                    {formatoComputador === 'Torre' ? (
                      <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-blue-500 uppercase tracking-widest ml-1">Monitor</label><select name="incluyeMonitor" className="w-full p-3 rounded-xl bg-white border border-blue-100 outline-none focus:border-blue-400 font-bold text-slate-700"><option>Sin Monitor</option><option>Con Monitor</option></select></div>
                    ) : (<div className="col-span-2 md:col-span-1"></div>)}
                    
                    <div><label className="text-[10px] font-black text-blue-500 uppercase tracking-widest ml-1">Procesador</label><select name="procesador" className="w-full p-3 rounded-xl bg-white border border-blue-100 outline-none focus:border-blue-400 font-bold text-slate-700"><option>Core i3</option><option>Core i5</option><option>Core i7</option><option>Ryzen 5</option><option>Apple M1/M2</option></select></div>
                    <div><label className="text-[10px] font-black text-blue-500 uppercase tracking-widest ml-1">RAM</label><select name="ram" className="w-full p-3 rounded-xl bg-white border border-blue-100 outline-none focus:border-blue-400 font-bold text-slate-700"><option>4GB</option><option>8GB</option><option>12GB</option><option>16GB</option><option>32GB</option></select></div>
                    <div><label className="text-[10px] font-black text-blue-500 uppercase tracking-widest ml-1">Tipo RAM</label><select name="tipoRam" className="w-full p-3 rounded-xl bg-white border border-blue-100 outline-none focus:border-blue-400 font-bold text-slate-700"><option>DDR3</option><option>DDR4</option><option>DDR5</option></select></div>
                    
                    <div><label className="text-[10px] font-black text-blue-500 uppercase tracking-widest ml-1">Disco Duro</label><select name="disco" className="w-full p-3 rounded-xl bg-white border border-blue-100 outline-none focus:border-blue-400 font-bold text-slate-700"><option>128GB</option><option>256GB</option><option>280GB</option><option>320GB</option><option>480GB</option><option>512GB</option><option>1TB</option></select></div>
                    <div><label className="text-[10px] font-black text-blue-500 uppercase tracking-widest ml-1">Tipo Disco</label><select name="tipoDisco" className="w-full p-3 rounded-xl bg-white border border-blue-100 outline-none focus:border-blue-400 font-bold text-slate-700"><option>SSD NVMe</option><option>SSD SATA</option><option>HDD</option></select></div>
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-blue-500 uppercase tracking-widest ml-1">SO</label><select name="so" className="w-full p-3 rounded-xl bg-white border border-blue-100 outline-none focus:border-blue-400 font-bold text-slate-700"><option>Win 10</option><option>Win 11</option><option>macOS</option></select></div>
                  </div>
                )}

                {/* IMPRESORAS */}
                {tipoRegistro === 'Impresoras' && (
                  <div className="p-6 bg-emerald-50/50 rounded-3xl border border-emerald-100 grid grid-cols-2 md:grid-cols-4 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-2 md:col-span-4 mb-2 border-b border-emerald-100 pb-2"><h4 className="font-black text-emerald-800 flex items-center gap-2"><Printer size={18}/> Ficha de Impresión</h4></div>
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-emerald-600 uppercase tracking-widest ml-1">Marca</label><select name="marcaImpresora" value={marcaImpresoraForm} onChange={e=>setMarcaImpresoraForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-emerald-100 outline-none focus:border-emerald-400 font-bold text-slate-700"><option>HP</option><option>Epson</option><option>Canon</option><option>Brother</option><option>Kyocera</option><option>Ricoh</option><option>Otro</option></select></div>
                    {marcaImpresoraForm === 'Otro' && <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-rose-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="marcaImpresoraOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-emerald-600 uppercase tracking-widest ml-1">Modelo</label><input name="modeloImpresora" placeholder="Ej: L3150" required className="w-full p-3 rounded-xl bg-white border border-emerald-100 outline-none focus:border-emerald-400 font-medium text-slate-700" /></div>
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-emerald-600 uppercase tracking-widest ml-1">Tipo</label><select name="tipoImpresora" value={tipoImpresoraForm} onChange={e=>setTipoImpresoraForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-emerald-100 outline-none focus:border-emerald-400 font-bold text-slate-700"><option>Láser</option><option>Inyección de Tinta</option><option>Matricial</option><option>Térmica</option><option>Multifuncional</option><option>Otro</option></select></div>
                    {tipoImpresoraForm === 'Otro' && <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-rose-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="tipoImpresoraOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-emerald-600 uppercase tracking-widest ml-1">Tóner / Tinta Ref.</label><input name="toner" placeholder="Ej: T664" className="w-full p-3 rounded-xl bg-white border border-emerald-100 outline-none focus:border-emerald-400 font-medium text-slate-700" /></div>
                    <div><label className="text-[10px] font-black text-emerald-600 uppercase tracking-widest ml-1">Proveedor Ext.</label><select name="esDeProveedor" className="w-full p-3 rounded-xl bg-white border border-emerald-100 outline-none focus:border-emerald-400 font-bold text-slate-700"><option>No</option><option>Sí</option></select></div>
                  </div>
                )}

                {/* TELEVISORES */}
                {tipoRegistro === 'Televisores' && (
                  <div className="p-6 bg-amber-50/50 rounded-3xl border border-amber-100 grid grid-cols-2 md:grid-cols-4 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-2 md:col-span-4 mb-2 border-b border-amber-100 pb-2"><h4 className="font-black text-amber-800 flex items-center gap-2"><Tv size={18}/> Especificaciones de TV</h4></div>
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-amber-600 uppercase tracking-widest ml-1">Uso</label><select name="usoTv" value={usoTvForm} onChange={e=>setUsoTvForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-amber-100 outline-none focus:border-amber-400 font-bold text-slate-700"><option>Habitación</option><option>Oficina</option><option>Pantalla Publicitaria</option></select></div>
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-amber-600 uppercase tracking-widest ml-1">Detalle Lógico (Piso/Hab)</label><input name="detalleUbicacionTv" required placeholder="Ej: 304" className="w-full p-3 rounded-xl bg-white border border-amber-100 outline-none focus:border-amber-400 font-medium text-slate-700" /></div>
                    
                    <div><label className="text-[10px] font-black text-amber-600 uppercase tracking-widest ml-1">Marca</label><select name="marcaTv" value={marcaTvForm} onChange={e=>setMarcaTvForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-amber-100 outline-none focus:border-amber-400 font-bold text-slate-700"><option>Samsung</option><option>LG</option><option>TCL</option><option>Hisense</option><option>Otro</option></select></div>
                    {marcaTvForm === 'Otro' && <div><label className="text-[10px] font-black text-rose-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="marcaTvOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-amber-600 uppercase tracking-widest ml-1">Modelo</label><input name="modeloTv" placeholder="Opcional" className="w-full p-3 rounded-xl bg-white border border-amber-100 outline-none focus:border-amber-400 font-medium text-slate-700" /></div>
                    <div><label className="text-[10px] font-black text-amber-600 uppercase tracking-widest ml-1">Tamaño</label><select name="tamanoTv" className="w-full p-3 rounded-xl bg-white border border-amber-100 outline-none focus:border-amber-400 font-bold text-slate-700"><option>24"</option><option>32"</option><option>40"</option><option>43"</option><option>50"</option><option>55"</option><option>65"</option></select></div>
                    
                    <div><label className="text-[10px] font-black text-amber-600 uppercase tracking-widest ml-1">Smart TV</label><select name="smartTv" className="w-full p-3 rounded-xl bg-white border border-amber-100 outline-none focus:border-amber-400 font-bold text-slate-700"><option>Sí</option><option>No</option></select></div>
                    <div><label className="text-[10px] font-black text-amber-600 uppercase tracking-widest ml-1">Deco Claro</label><select name="decodClaro" className="w-full p-3 rounded-xl bg-white border border-amber-100 outline-none focus:border-amber-400 font-bold text-slate-700"><option>No</option><option>Sí</option></select></div>
                    <div><label className="text-[10px] font-black text-amber-600 uppercase tracking-widest ml-1">Deco DirecTV</label><select name="directTv" className="w-full p-3 rounded-xl bg-white border border-amber-100 outline-none focus:border-amber-400 font-bold text-slate-700"><option>No</option><option>Sí</option></select></div>
                    <div><label className="text-[10px] font-black text-amber-600 uppercase tracking-widest ml-1">N° Controles</label><select name="cantidadControles" className="w-full p-3 rounded-xl bg-white border border-amber-100 outline-none focus:border-amber-400 font-bold text-slate-700"><option>1</option><option>2</option><option>3</option><option>0</option></select></div>
                    
                    <div className="col-span-2 md:col-span-4 mt-2">
                      <p className="text-[10px] font-black text-amber-600 uppercase tracking-widest mb-3">Plataformas Apps (Clic para añadir)</p>
                      <div className="flex flex-wrap gap-2">
                        {['Netflix', 'Disney+', 'Youtube', 'Spotify', 'HBO Max'].map(app => (
                          <button type="button" key={app} onClick={() => toggleTvPlataforma(app)} className={`px-4 py-2 rounded-xl text-xs font-bold transition-all border ${tvPlataformas.includes(app) ? 'bg-amber-500 text-white border-amber-600 shadow-md' : 'bg-white text-slate-600 border-slate-200 hover:bg-amber-50'}`}>
                            {tvPlataformas.includes(app) && '✓ '} {app}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* ACCESS POINT (AP) */}
                {tipoRegistro === 'AP' && (
                  <div className="p-6 bg-purple-50/50 rounded-3xl border border-purple-100 grid grid-cols-2 md:grid-cols-3 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-2 md:col-span-3 mb-2 border-b border-purple-100 pb-2"><h4 className="font-black text-purple-800 flex items-center gap-2"><Wifi size={18}/> Access Point</h4></div>
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-purple-600 uppercase tracking-widest ml-1">Marca</label><select name="marcaAp" value={marcaApForm} onChange={e=>setMarcaApForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-purple-100 outline-none focus:border-purple-400 font-bold text-slate-700"><option>Ubiquiti</option><option>Sophos</option><option>Cisco</option><option>Aruba</option><option>Otro</option></select></div>
                    {marcaApForm === 'Otro' && <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-rose-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="marcaApOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-purple-600 uppercase tracking-widest ml-1">Modelo</label><input name="modeloAp" required className="w-full p-3 rounded-xl bg-white border border-purple-100 outline-none focus:border-purple-400" /></div>
                    <div><label className="text-[10px] font-black text-purple-600 uppercase tracking-widest ml-1">Piso Numérico</label><input name="pisoAp" type="number" required placeholder="Ej: 3" className="w-full p-3 rounded-xl bg-white border border-purple-100 outline-none focus:border-purple-400" /></div>
                    <div><label className="text-[10px] font-black text-purple-600 uppercase tracking-widest ml-1">N° de AP</label><select name="numAp" className="w-full p-3 rounded-xl bg-white border border-purple-100 outline-none focus:border-purple-400 font-bold text-slate-700"><option>1</option><option>2</option><option>3</option><option>4</option><option>8</option></select></div>
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-purple-600 uppercase tracking-widest ml-1">Sector (Ref)</label><input name="sectorAp" required placeholder="Ej: Pasillo" className="w-full p-3 rounded-xl bg-white border border-purple-100 outline-none focus:border-purple-400" /></div>
                  </div>
                )}

                {/* SWITCH */}
                {tipoRegistro === 'Switch' && (
                  <div className="p-6 bg-indigo-50/50 rounded-3xl border border-indigo-100 grid grid-cols-2 md:grid-cols-4 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-2 md:col-span-4 mb-2 border-b border-indigo-100 pb-2"><h4 className="font-black text-indigo-800 flex items-center gap-2"><Radio size={18}/> Switch de Red</h4></div>
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest ml-1">Marca</label><select name="marcaSwitch" value={marcaSwitchForm} onChange={e=>setMarcaSwitchForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-indigo-100 outline-none focus:border-indigo-400 font-bold text-slate-700"><option>Cisco</option><option>Aruba</option><option>Ubiquiti</option><option>Sophos</option><option>TP-Link</option><option>MikroTik</option><option>Otro</option></select></div>
                    {marcaSwitchForm === 'Otro' && <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-rose-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="marcaSwitchOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest ml-1">Modelo</label><input name="modeloSwitch" required placeholder="Ej: SG110" className="w-full p-3 rounded-xl bg-white border border-indigo-100 outline-none focus:border-indigo-400" /></div>
                    <div><label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest ml-1">Puertos</label><select name="puertosSwitch" className="w-full p-3 rounded-xl bg-white border border-indigo-100 outline-none focus:border-indigo-400 font-bold text-slate-700"><option>4</option><option>5</option><option>8</option><option>16</option><option>24</option><option>48</option><option>52</option></select></div>
                    <div><label className="text-[10px] font-black text-indigo-600 uppercase tracking-widest ml-1">¿Tiene PoE?</label><select name="poeSwitch" className="w-full p-3 rounded-xl bg-white border border-indigo-100 outline-none focus:border-indigo-400 font-bold text-slate-700"><option>Sí</option><option>No</option></select></div>
                  </div>
                )}

                {/* PLANTA TELEFÓNICA */}
                {tipoRegistro === 'Planta Telefónica' && (
                  <div className="p-6 bg-pink-50/50 rounded-3xl border border-pink-100 grid grid-cols-1 sm:grid-cols-3 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-1 sm:col-span-3 mb-2 border-b border-pink-100 pb-2"><h4 className="font-black text-pink-800 flex items-center gap-2"><Phone size={18}/> Planta Telefónica</h4></div>
                    
                    <div><label className="text-[10px] font-black text-pink-600 uppercase tracking-widest ml-1">Marca</label><select name="marcaPlanta" value={marcaPlantaForm} onChange={e=>setMarcaPlantaForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-pink-100 outline-none focus:border-pink-400 font-bold text-slate-700"><option>Mitel</option><option>Grandstream</option><option>Panasonic</option><option>Otro</option></select></div>
                    {marcaPlantaForm === 'Otro' && <div><label className="text-[10px] font-black text-rose-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="marcaPlantaOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    
                    <div><label className="text-[10px] font-black text-pink-600 uppercase tracking-widest ml-1">Tecnología</label><select name="tipoPlanta" className="w-full p-3 rounded-xl bg-white border border-pink-100 outline-none focus:border-pink-400 font-bold text-slate-700"><option>IP (VoIP)</option><option>Análoga</option></select></div>
                    <div><label className="text-[10px] font-black text-pink-600 uppercase tracking-widest ml-1">Total Extensiones</label><input name="extensionesPlanta" type="number" required placeholder="Ej: 32" className="w-full p-3 rounded-xl bg-white border border-pink-100 outline-none focus:border-pink-400" /></div>
                  </div>
                )}

                {/* TELÉFONOS IP */}
                {tipoRegistro === 'Teléfonos IP' && (
                  <div className="p-6 bg-cyan-50/50 rounded-3xl border border-cyan-100 grid grid-cols-2 md:grid-cols-4 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-2 md:col-span-4 mb-2 border-b border-cyan-100 pb-2"><h4 className="font-black text-cyan-800 flex items-center gap-2"><Phone size={18}/> Teléfono IP</h4></div>
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-cyan-600 uppercase tracking-widest ml-1">Marca</label><select name="marcaTelefonoIP" value={marcaTelefonoIPForm} onChange={e=>setMarcaTelefonoIPForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-cyan-100 outline-none focus:border-cyan-400 font-bold text-slate-700"><option>Mitel</option><option>Grandstream</option><option>Cisco</option><option>Yealink</option><option>Otro</option></select></div>
                    {marcaTelefonoIPForm === 'Otro' && <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-rose-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="marcaTelefonoIPOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-cyan-600 uppercase tracking-widest ml-1">Modelo</label><input name="modeloTelefonoIP" required placeholder="Ej: 6920" className="w-full p-3 rounded-xl bg-white border border-cyan-100 outline-none focus:border-cyan-400" /></div>
                    <div><label className="text-[10px] font-black text-cyan-600 uppercase tracking-widest ml-1">Extensión</label><input name="extensionTelefonoIP" required placeholder="Ej: 101" className="w-full p-3 rounded-xl bg-white border border-cyan-100 outline-none focus:border-cyan-400 text-blue-600 font-bold" /></div>
                    <div><label className="text-[10px] font-black text-cyan-600 uppercase tracking-widest ml-1">Energía PoE</label><select name="poeTelefonoIP" className="w-full p-3 rounded-xl bg-white border border-cyan-100 outline-none focus:border-cyan-400 font-bold text-slate-700"><option>Sí (PoE)</option><option>No (Adaptador)</option></select></div>
                  </div>
                )}

                {/* NVR / DVR */}
                {tipoRegistro === 'NVR / DVR' && (
                  <div className="p-6 bg-slate-100/80 rounded-3xl border border-slate-200 grid grid-cols-1 md:grid-cols-3 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-1 md:col-span-3 mb-2 border-b border-slate-200 pb-2"><h4 className="font-black text-slate-800 flex items-center gap-2"><HardDrive size={18}/> Grabador de Video</h4></div>
                    <div><label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Tipo</label><select name="tipoNvr" className="w-full p-3 rounded-xl bg-white border border-slate-200 outline-none focus:border-blue-400 font-bold text-slate-700"><option>NVR (Red/IP)</option><option>DVR (Análogo)</option></select></div>
                    <div><label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Canales</label><select name="canalesNvr" className="w-full p-3 rounded-xl bg-white border border-slate-200 outline-none focus:border-blue-400 font-bold text-slate-700"><option>16</option><option>32</option><option>64</option></select></div>
                    <div><label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Capacidad Disco</label><select name="discoNvr" className="w-full p-3 rounded-xl bg-white border border-slate-200 outline-none focus:border-blue-400 font-bold text-slate-700"><option>4TB</option><option>8TB</option><option>12TB</option><option>16TB</option></select></div>
                  </div>
                )}

                {/* CÁMARAS DE SEGURIDAD */}
                {tipoRegistro === 'Cámaras de seguridad' && (
                  <div className="p-6 bg-slate-100/80 rounded-3xl border border-slate-200 grid grid-cols-1 md:grid-cols-3 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-1 md:col-span-3 mb-2 border-b border-slate-200 pb-2"><h4 className="font-black text-slate-800 flex items-center gap-2"><Camera size={18}/> Cámara</h4></div>
                    <div><label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Formato</label><select name="tipoCamara" className="w-full p-3 rounded-xl bg-white border border-slate-200 outline-none focus:border-blue-400 font-bold text-slate-700"><option>Domo</option><option>Bala</option><option>PTZ</option></select></div>
                    <div><label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Tecnología</label><select name="tecnologiaCamara" className="w-full p-3 rounded-xl bg-white border border-slate-200 outline-none focus:border-blue-400 font-bold text-slate-700"><option>IP / Red</option><option>Análoga</option></select></div>
                    <div><label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Conectada al NVR/DVR</label><input name="nvrDvr" required placeholder="Ej: NVR Principal" className="w-full p-3 rounded-xl bg-white border border-slate-200 outline-none focus:border-blue-400" /></div>
                  </div>
                )}

                {/* AUDIOVISUALES */}
                {tipoRegistro === 'Audiovisuales' && (
                  <div className="p-6 bg-rose-50/50 rounded-3xl border border-rose-100 grid grid-cols-1 md:grid-cols-3 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-1 md:col-span-3 mb-2 border-b border-rose-100 pb-2"><h4 className="font-black text-rose-800 flex items-center gap-2"><Box size={18}/> Equipos Audiovisuales</h4></div>
                    <div>
                      <label className="text-[10px] font-black text-rose-600 uppercase tracking-widest ml-1">Dispositivo</label>
                      <select name="subtipoAudiovisual" value={subtipoAudiovisualForm} onChange={e=>setSubtipoAudiovisualForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-rose-100 outline-none focus:border-rose-400 font-bold text-slate-700">
                        <option>Amplificador</option><option>Consola de audio</option><option>Parlantes</option><option>Luces</option><option>Auriculares</option><option>Micrófonos</option><option>Otro</option>
                      </select>
                    </div>
                    {subtipoAudiovisualForm === 'Otro' && <div><label className="text-[10px] font-black text-red-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="subtipoAudiovisualOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    <div><label className="text-[10px] font-black text-rose-600 uppercase tracking-widest ml-1">Marca</label><input name="marcaAudiovisual" required placeholder="Ej: Yamaha, Shure" className="w-full p-3 rounded-xl bg-white border border-rose-100 outline-none focus:border-rose-400" /></div>
                    <div><label className="text-[10px] font-black text-rose-600 uppercase tracking-widest ml-1">Modelo</label><input name="modeloAudiovisual" required placeholder="Ej: MG16XU" className="w-full p-3 rounded-xl bg-white border border-rose-100 outline-none focus:border-rose-400" /></div>
                  </div>
                )}

                {/* TABLET */}
                {tipoRegistro === 'Tablet' && (
                  <div className="p-6 bg-orange-50/50 rounded-3xl border border-orange-100 grid grid-cols-2 md:grid-cols-4 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-2 md:col-span-4 mb-2 border-b border-orange-100 pb-2"><h4 className="font-black text-orange-800 flex items-center gap-2"><Tablet size={18}/> Tablet</h4></div>
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1">Marca</label><select name="marcaTablet" value={marcaTabletForm} onChange={e=>setMarcaTabletForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400 font-bold text-slate-700"><option>Samsung</option><option>Apple (iPad)</option><option>Lenovo</option><option>Huawei</option><option>Xiaomi</option><option>Amazon (Fire)</option><option>Otro</option></select></div>
                    {marcaTabletForm === 'Otro' && <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-rose-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="marcaTabletOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1">Modelo</label><input name="modeloTablet" required placeholder="Ej: Galaxy Tab S6 Lite" className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400" /></div>
                    <div><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1">Tamaño</label><select name="tamanoTablet" className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400 font-bold text-slate-700"><option>7"</option><option>8"</option><option>8.7"</option><option>9.7"</option><option>10.1"</option><option>10.4"</option><option>10.5"</option><option>11"</option><option>12.4"</option><option>12.9"</option></select></div>
                    
                    <div><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1">Procesador</label><select name="procesadorTablet" className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400 font-bold text-slate-700"><option>Snapdragon</option><option>MediaTek</option><option>Exynos</option><option>Apple A/M Series</option><option>Unisoc</option><option>Intel / AMD</option><option>Otro</option></select></div>
                    <div><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1">RAM</label><select name="ramTablet" className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400 font-bold text-slate-700"><option>2GB</option><option>3GB</option><option>4GB</option><option>6GB</option><option>8GB</option><option>12GB</option><option>16GB</option></select></div>
                    <div><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1">Almacenamiento</label><select name="almacenamientoTablet" className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400 font-bold text-slate-700"><option>32GB</option><option>64GB</option><option>128GB</option><option>256GB</option><option>512GB</option><option>1TB</option><option>2TB</option></select></div>
                    
                    <div><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1">Forro</label><select name="forroTablet" className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400 font-bold text-slate-700"><option>Sí</option><option>No</option></select></div>
                    <div><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1">Vidrio T.</label><select name="vidrioTablet" className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400 font-bold text-slate-700"><option>Sí</option><option>No</option></select></div>
                    
                    <div className="col-span-2 md:col-span-2"><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1">E-mail</label><input name="emailDispositivo" type="email" placeholder="Ej: equipo@empresa.com" className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400" /></div>
                    <div className="col-span-2 md:col-span-2"><label className="text-[10px] font-black text-orange-600 uppercase tracking-widest ml-1"># de Celular (SIM)</label><input name="numeroCelular" type="tel" placeholder="Ej: +57 3001234567" className="w-full p-3 rounded-xl bg-white border border-orange-100 outline-none focus:border-orange-400" /></div>
                  </div>
                )}

                {/* CELULARES */}
                {tipoRegistro === 'Celulares' && (
                  <div className="p-6 bg-teal-50/50 rounded-3xl border border-teal-100 grid grid-cols-2 md:grid-cols-4 gap-4 animate-in fade-in zoom-in duration-300">
                    <div className="col-span-2 md:col-span-4 mb-2 border-b border-teal-100 pb-2"><h4 className="font-black text-teal-800 flex items-center gap-2"><Smartphone size={18}/> Celular / Smartphone</h4></div>
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1">Marca</label><select name="marcaCelular" value={marcaCelularForm} onChange={e=>setMarcaCelularForm(e.target.value)} className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400 font-bold text-slate-700"><option>Samsung</option><option>Apple (iPhone)</option><option>Xiaomi</option><option>Motorola</option><option>Oppo</option><option>Vivo</option><option>Honor</option><option>Otro</option></select></div>
                    {marcaCelularForm === 'Otro' && <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-rose-500 uppercase tracking-widest ml-1">¿Cuál?</label><input name="marcaCelularOtro" className="w-full p-3 rounded-xl bg-rose-50 border border-rose-200 outline-none" required /></div>}
                    
                    <div className="col-span-2 md:col-span-1"><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1">Modelo</label><input name="modeloCelular" required placeholder="Ej: Galaxy S23" className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400" /></div>
                    <div><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1">Pantalla</label><select name="tamanoCelular" className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400 font-bold text-slate-700"><option>5.5"</option><option>5.8"</option><option>6.1"</option><option>6.4"</option><option>6.7"</option><option>6.8"</option><option>6.9"</option></select></div>
                    
                    <div><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1">Procesador</label><select name="procesadorCelular" className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400 font-bold text-slate-700"><option>Snapdragon</option><option>MediaTek</option><option>Exynos</option><option>Apple A-Series</option><option>Unisoc</option><option>Otro</option></select></div>
                    <div><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1">RAM</label><select name="ramCelular" className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400 font-bold text-slate-700"><option>2GB</option><option>3GB</option><option>4GB</option><option>6GB</option><option>8GB</option><option>12GB</option><option>16GB</option></select></div>
                    <div><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1">Almacenamiento</label><select name="almacenamientoCelular" className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400 font-bold text-slate-700"><option>32GB</option><option>64GB</option><option>128GB</option><option>256GB</option><option>512GB</option><option>1TB</option></select></div>
                    
                    <div><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1">Forro</label><select name="forroCelular" className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400 font-bold text-slate-700"><option>Sí</option><option>No</option></select></div>
                    <div><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1">Vidrio T.</label><select name="vidrioCelular" className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400 font-bold text-slate-700"><option>Sí</option><option>No</option></select></div>
                    
                    <div className="col-span-2 md:col-span-2"><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1">E-mail</label><input name="emailDispositivo" type="email" placeholder="Ej: equipo@empresa.com" className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400" /></div>
                    <div className="col-span-2 md:col-span-2"><label className="text-[10px] font-black text-teal-600 uppercase tracking-widest ml-1"># de Celular (Línea)</label><input name="numeroCelular" type="tel" placeholder="Ej: +57 3001234567" className="w-full p-3 rounded-xl bg-white border border-teal-100 outline-none focus:border-teal-400" /></div>
                  </div>
                )}

                {/* OTRO GENÉRICO */}
                {tipoRegistro === 'Otro' && (
                  <div className="space-y-2 animate-in fade-in zoom-in duration-300 bg-slate-50 p-6 rounded-3xl border border-slate-200">
                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Descripción / Especificaciones</label>
                    <textarea name="descripcionOtro" rows="3" className="w-full p-4 rounded-2xl bg-white border border-slate-200 focus:border-blue-400 outline-none font-medium resize-none text-slate-700" placeholder="Ingresa los detalles técnicos relevantes de este equipo..." required></textarea>
                  </div>
                )}
                {/* --- FIN CAMPOS DINÁMICOS --- */}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Para AP y TV la ubicación es automática a partir de sus propios campos */}
                  {tipoRegistro !== 'Televisores' && tipoRegistro !== 'AP' ? (
                    <div className="space-y-2">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Ubicación Física</label>
                      <input name="ubicacion" className="w-full p-4 rounded-2xl bg-slate-50 border-2 border-slate-50 focus:border-blue-400 outline-none font-medium" placeholder="Ej: Sala de juntas 2do Piso" required />
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Ubicación</label>
                      <input disabled placeholder="Se genera automáticamente con los datos técnicos" className="w-full p-4 rounded-2xl bg-slate-100 border-2 border-slate-100 text-slate-400 font-medium cursor-not-allowed" />
                    </div>
                  )}
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Responsable / Usuario</label>
                    <input name="responsable" className="w-full p-4 rounded-2xl bg-slate-50 border-2 border-slate-50 focus:border-blue-400 outline-none font-medium" placeholder="Ej: Ing. Marco Antonio" />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Fotografía del Activo</label>
                  <div className="p-8 bg-slate-50 rounded-3xl border-2 border-dashed border-slate-200 flex flex-col items-center gap-4 group hover:bg-white hover:border-blue-400 transition-all cursor-pointer">
                    <ImageIcon className="text-slate-300 group-hover:text-blue-500 group-hover:scale-110 transition-all" size={48} />
                    <div className="text-center">
                      <p className="text-sm font-black text-slate-600">Haz clic para subir imagen</p>
                      <p className="text-[10px] font-bold text-slate-400 uppercase mt-1">Formatos: JPG, PNG (Máx 2MB)</p>
                    </div>
                    <input type="file" name="foto" className="opacity-0 absolute w-full h-full cursor-pointer" accept="image/*" />
                  </div>
                </div>

                <div className="flex gap-4 pt-6">
                  <button type="button" onClick={() => setMostrarFormulario(false)} className="flex-1 py-5 rounded-[1.5rem] bg-slate-100 text-slate-600 font-black uppercase tracking-widest text-xs hover:bg-slate-200 transition-all">Cancelar</button>
                  <button type="submit" className="flex-1 py-5 rounded-[1.5rem] bg-blue-600 text-white font-black uppercase tracking-widest text-xs shadow-xl shadow-blue-200 hover:bg-blue-700 transition-all active:scale-95">Guardar Registro</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
