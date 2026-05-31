import { useState, useEffect, useRef } from "react";

// ─────────────────────────────────────────────
// SUPABASE CONFIG
// ─────────────────────────────────────────────
const SUPABASE_URL = "https://ncznhjadvddtezzawnzm.supabase.co";
const SUPABASE_KEY = "sb_publishable_voqutRHpn6wMVjyk532BWw_ubDBOn-F";

const sb = {
  headers: { "Content-Type": "application/json", "apikey": SUPABASE_KEY, "Authorization": `Bearer ${SUPABASE_KEY}` },
  url: (table, params = "") => `${SUPABASE_URL}/rest/v1/${table}${params}`,

  async get(table, params = "") {
    const r = await fetch(this.url(table, params), { headers: { ...this.headers, "Prefer": "return=representation" } });
    return r.json();
  },
  async post(table, data) {
    const r = await fetch(this.url(table), { method: "POST", headers: { ...this.headers, "Prefer": "return=representation" }, body: JSON.stringify(data) });
    return r.json();
  },
  async patch(table, id, data) {
    const r = await fetch(this.url(table, `?id=eq.${id}`), { method: "PATCH", headers: { ...this.headers, "Prefer": "return=representation" }, body: JSON.stringify(data) });
    return r.json();
  },
  async delete(table, id) {
    await fetch(this.url(table, `?id=eq.${id}`), { method: "DELETE", headers: this.headers });
  },
};

// ─────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────
const SERVICES = [
  { id: "marketing",   name: "Agencia de Marketing",      color: "#ff7a59", icon: "📣", meta: 500000,  precio: 15000 },
  { id: "incubadora",  name: "Incubadora de Negocios",    color: "#7c3aed", icon: "🥚", meta: 300000,  precio: 25000 },
  { id: "aceleradora", name: "Aceleradora de Negocios",   color: "#0ea5e9", icon: "🚀", meta: 400000,  precio: 35000 },
  { id: "software",    name: "Desarrollo de Software",    color: "#10b981", icon: "💻", meta: 600000,  precio: 50000 },
  { id: "inversiones", name: "Inversiones",               color: "#f59e0b", icon: "📈", meta: 1000000, precio: 100000 },
  { id: "creditos",    name: "Créditos PyME",             color: "#ef4444", icon: "🏦", meta: 80000,   precio: 80000 },
];

const ETAPAS = ["Nuevo Lead","Contactado","Cita Agendada","Propuesta Enviada","Negociación","Cerrado Ganado","Cerrado Perdido"];
const ETAPA_COLORS = {
  "Nuevo Lead":"#94a3b8","Contactado":"#60a5fa","Cita Agendada":"#a78bfa",
  "Propuesta Enviada":"#fb923c","Negociación":"#f59e0b","Cerrado Ganado":"#10b981","Cerrado Perdido":"#ef4444"
};
const STATUS_OPTIONS = [
  { id:"online",    label:"En línea",     color:"#10b981", icon:"🟢" },
  { id:"bathroom",  label:"Baño",         color:"#60a5fa", icon:"🚻" },
  { id:"food",      label:"Comida",       color:"#f59e0b", icon:"🍽️" },
  { id:"coaching",  label:"Coaching",     color:"#a78bfa", icon:"🎓" },
  { id:"offline",   label:"Desconectado", color:"#94a3b8", icon:"⚫" },
];

// ─────────────────────────────────────────────
// ML SCORING
// ─────────────────────────────────────────────
function mlScore(c) {
  let score = 30;
  if (c.etapa === "Negociación") score += 35;
  else if (c.etapa === "Propuesta Enviada") score += 25;
  else if (c.etapa === "Cita Agendada") score += 15;
  else if (c.etapa === "Contactado") score += 8;
  else if (c.etapa === "Cerrado Ganado") return 100;
  else if (c.etapa === "Cerrado Perdido") return 0;
  if ((c.interacciones || 0) > 5) score += 15;
  else if ((c.interacciones || 0) > 2) score += 8;
  const pos = ["interesado","confirmó","cuando","precio","listo","si","quiero"];
  const neg = ["no","ocupado","después","caro","pensar","difícil"];
  const notas = (c.notas || "").toLowerCase();
  pos.forEach(k => { if (notas.includes(k)) score += 4; });
  neg.forEach(k => { if (notas.includes(k)) score -= 5; });
  return Math.min(99, Math.max(1, score));
}
function scoreColor(s) {
  if (s >= 70) return { bg:"#dcfce7", text:"#166534", border:"#86efac", label:"Alta" };
  if (s >= 40) return { bg:"#fef3c7", text:"#92400e", border:"#fcd34d", label:"Media" };
  return { bg:"#fee2e2", text:"#991b1b", border:"#fca5a5", label:"Riesgo" };
}

// ─────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────
const fmt = n => new Intl.NumberFormat("es-MX",{style:"currency",currency:"MXN",maximumFractionDigits:0}).format(n);
function Avatar({initials,size=36,color="#ff7a59"}) {
  return <div style={{width:size,height:size,borderRadius:"50%",background:`linear-gradient(135deg,${color},${color}cc)`,display:"flex",alignItems:"center",justifyContent:"center",color:"#fff",fontWeight:800,fontSize:size*.35,flexShrink:0}}>{initials}</div>;
}
function Card({children,style={}}) {
  return <div style={{background:"#fff",borderRadius:12,border:"1px solid #f0f0f0",boxShadow:"0 1px 4px rgba(0,0,0,.06)",padding:20,...style}}>{children}</div>;
}
function ProgressBar({value,max,color,h=8}) {
  const pct = Math.min(100,Math.round((value/max)*100));
  return <div style={{width:"100%",height:h,background:"#f3f4f6",borderRadius:99}}><div style={{height:"100%",width:`${pct}%`,background:color||"#ff7a59",borderRadius:99,transition:"width .6s"}}/></div>;
}
function Spinner() {
  return <div style={{display:"flex",alignItems:"center",justifyContent:"center",padding:60}}><div style={{width:32,height:32,border:"3px solid #f0f0f0",borderTop:"3px solid #ff7a59",borderRadius:"50%",animation:"spin 1s linear infinite"}}/><style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style></div>;
}

// ─────────────────────────────────────────────
// LOGIN
// ─────────────────────────────────────────────
function Login({onLogin}) {
  const [email,setEmail] = useState("");
  const [pass,setPass] = useState("");
  const [error,setError] = useState("");
  const [loading,setLoading] = useState(false);

  const handle = async () => {
    setLoading(true); setError("");
    try {
      const data = await sb.get("usuarios",`?email=eq.${encodeURIComponent(email)}&password=eq.${encodeURIComponent(pass)}`);
      if (data && data.length > 0) onLogin(data[0]);
      else setError("Credenciales incorrectas");
    } catch(e) { setError("Error de conexión con Supabase"); }
    setLoading(false);
  };

  const demoUsers = [
    {name:"Admin",email:"admin@empresa.com",pass:"admin123"},
    {name:"Carlos",email:"carlos@empresa.com",pass:"vendedor1"},
    {name:"Sofía",email:"sofia@empresa.com",pass:"vendedor2"},
    {name:"Diego",email:"diego@empresa.com",pass:"vendedor3"},
  ];

  return (
    <div style={{minHeight:"100vh",background:"linear-gradient(135deg,#0f0c29,#302b63,#24243e)",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"'DM Sans',system-ui,sans-serif"}}>
      <div style={{background:"rgba(255,255,255,.06)",backdropFilter:"blur(20px)",border:"1px solid rgba(255,255,255,.12)",borderRadius:20,padding:"44px 36px",width:360,boxShadow:"0 30px 80px rgba(0,0,0,.4)"}}>
        <div style={{textAlign:"center",marginBottom:28}}>
          <div style={{width:54,height:54,background:"linear-gradient(135deg,#ff7a59,#ff9a7b)",borderRadius:16,display:"flex",alignItems:"center",justifyContent:"center",fontSize:26,margin:"0 auto 14px"}}>🚀</div>
          <h1 style={{color:"#fff",margin:0,fontSize:22,fontWeight:800}}>CRM Enterprise</h1>
          <p style={{color:"rgba(255,255,255,.5)",margin:"6px 0 0",fontSize:12}}>Conectado a Supabase ✅</p>
        </div>
        {error && <div style={{background:"#fee2e2",color:"#991b1b",padding:"10px 14px",borderRadius:8,fontSize:13,marginBottom:14,textAlign:"center"}}>{error}</div>}
        <div style={{display:"flex",flexDirection:"column",gap:12}}>
          <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" type="email"
            style={{padding:"11px 14px",borderRadius:10,border:"1px solid rgba(255,255,255,.2)",background:"rgba(255,255,255,.08)",color:"#fff",fontSize:13,outline:"none"}}/>
          <input value={pass} onChange={e=>setPass(e.target.value)} placeholder="Contraseña" type="password"
            onKeyDown={e=>e.key==="Enter"&&handle()}
            style={{padding:"11px 14px",borderRadius:10,border:"1px solid rgba(255,255,255,.2)",background:"rgba(255,255,255,.08)",color:"#fff",fontSize:13,outline:"none"}}/>
          <button onClick={handle} disabled={loading}
            style={{padding:"12px",background:"linear-gradient(135deg,#ff7a59,#ff9a7b)",color:"#fff",border:"none",borderRadius:10,fontSize:14,fontWeight:800,cursor:"pointer",opacity:loading?.7:1}}>
            {loading?"Conectando...":"Iniciar Sesión"}
          </button>
        </div>
        <div style={{marginTop:20,borderTop:"1px solid rgba(255,255,255,.1)",paddingTop:16}}>
          <p style={{color:"rgba(255,255,255,.4)",fontSize:11,margin:"0 0 8px",textAlign:"center"}}>Acceso rápido:</p>
          <div style={{display:"flex",gap:6,flexWrap:"wrap"}}>
            {demoUsers.map(u=>(
              <button key={u.email} onClick={()=>{setEmail(u.email);setPass(u.pass);}}
                style={{flex:1,minWidth:70,padding:"6px 8px",background:"rgba(255,255,255,.08)",border:"1px solid rgba(255,255,255,.15)",borderRadius:7,color:"rgba(255,255,255,.7)",fontSize:11,cursor:"pointer",fontWeight:600}}>
                {u.name}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// DASHBOARD ADMIN
// ─────────────────────────────────────────────
function DashboardAdmin({contacts,usuarios,metas}) {
  const ganados = contacts.filter(c=>c.etapa==="Cerrado Ganado");
  const totalVentas = ganados.reduce((s,c)=>s+c.valor,0);
  const pipeline = contacts.filter(c=>!["Cerrado Ganado","Cerrado Perdido"].includes(c.etapa)).reduce((s,c)=>s+c.valor*(mlScore(c)/100),0);

  const DAILY = [{d:"Lun",v:65000},{d:"Mar",v:120000},{d:"Mié",v:85000},{d:"Jue",v:195000},{d:"Vie",v:140000},{d:"Sáb",v:45000}];
  const maxD = Math.max(...DAILY.map(d=>d.v));
  const SOCIAL = [
    {p:"Meta Ads",inv:15000,leads:87,conv:12,color:"#1877f2"},
    {p:"Google Ads",inv:22000,leads:134,conv:23,color:"#ea4335"},
    {p:"LinkedIn",inv:8000,leads:31,conv:8,color:"#0a66c2"},
    {p:"TikTok",inv:5000,leads:210,conv:7,color:"#ff0050"},
  ];

  return (
    <div style={{display:"flex",flexDirection:"column",gap:20}}>
      <div style={{display:"flex",gap:14,flexWrap:"wrap"}}>
        {[
          {label:"Ventas del Mes",value:fmt(totalVentas),icon:"💰",sub:"+12% vs mes anterior",color:"#ff7a59"},
          {label:"Pipeline IA",value:fmt(pipeline),icon:"🤖",sub:"Score ML ponderado",color:"#7c3aed"},
          {label:"Total Leads",value:contacts.length,icon:"👥",sub:`${contacts.filter(c=>c.etapa==="Nuevo Lead").length} nuevos`,color:"#0ea5e9"},
          {label:"Tasa de Cierre",value:`${contacts.length?Math.round((ganados.length/contacts.length)*100):0}%`,icon:"🎯",sub:"Meta: 35%",color:"#10b981"},
        ].map(s=>(
          <div key={s.label} style={{flex:1,minWidth:150,background:"#fff",borderRadius:12,padding:"18px 20px",border:"1px solid #f0f0f0",boxShadow:"0 1px 4px rgba(0,0,0,.06)"}}>
            <div style={{display:"flex",justifyContent:"space-between"}}><span style={{fontSize:11,color:"#6b7280",fontWeight:600}}>{s.label}</span><span style={{fontSize:20}}>{s.icon}</span></div>
            <div style={{fontSize:26,fontWeight:800,color:"#111827",margin:"8px 0 4px",letterSpacing:"-1px"}}>{s.value}</div>
            <div style={{fontSize:11,color:s.color,fontWeight:600}}>{s.sub}</div>
          </div>
        ))}
      </div>

      <div style={{display:"flex",gap:20,flexWrap:"wrap"}}>
        <Card style={{flex:2,minWidth:260}}>
          <h3 style={{margin:"0 0 14px",fontSize:14,fontWeight:700}}>📊 Ventas Diarias</h3>
          <div style={{display:"flex",gap:8,alignItems:"flex-end",height:110}}>
            {DAILY.map(d=>(
              <div key={d.d} style={{flex:1,display:"flex",flexDirection:"column",alignItems:"center",gap:4}}>
                <span style={{fontSize:9,color:"#6b7280",fontWeight:600}}>{fmt(d.v).replace("$","").replace(",000","k")}</span>
                <div style={{width:"100%",borderRadius:"5px 5px 0 0",background:"linear-gradient(to top,#ff7a59,#ffb49a)",height:`${(d.v/maxD)*100}px`,minHeight:4}}/>
                <span style={{fontSize:10,color:"#9ca3af",fontWeight:700}}>{d.d}</span>
              </div>
            ))}
          </div>
        </Card>
        <Card style={{flex:1,minWidth:200}}>
          <h3 style={{margin:"0 0 12px",fontSize:14,fontWeight:700}}>🟢 Equipo en Vivo</h3>
          {usuarios.filter(u=>u.rol==="vendedor").map(v=>{
            const st = STATUS_OPTIONS.find(s=>s.id===v.status)||STATUS_OPTIONS[0];
            return (
              <div key={v.id} style={{display:"flex",alignItems:"center",gap:8,padding:"8px 10px",borderRadius:8,background:"#f9fafb",marginBottom:6}}>
                <div style={{position:"relative"}}><Avatar initials={v.avatar||v.nombre.slice(0,2).toUpperCase()} size={30} color={v.color||"#ff7a59"}/><div style={{position:"absolute",bottom:0,right:0,width:9,height:9,borderRadius:"50%",background:st.color,border:"2px solid #fff"}}/></div>
                <div><div style={{fontSize:12,fontWeight:700,color:"#111827"}}>{v.nombre}</div><div style={{fontSize:10,color:"#6b7280"}}>{st.icon} {st.label}</div></div>
              </div>
            );
          })}
        </Card>
      </div>

      <Card>
        <h3 style={{margin:"0 0 14px",fontSize:14,fontWeight:700}}>🎯 Metas por Servicio</h3>
        {SERVICES.map(s=>{
          const ganado = contacts.filter(c=>c.servicio===s.id&&c.etapa==="Cerrado Ganado").reduce((a,c)=>a+c.valor,0);
          const meta = metas[s.id]||s.meta;
          const pct = Math.round((ganado/meta)*100);
          return (
            <div key={s.id} style={{marginBottom:14}}>
              <div style={{display:"flex",justifyContent:"space-between",marginBottom:5}}>
                <span style={{fontSize:13,fontWeight:600}}>{s.icon} {s.name}</span>
                <span style={{fontSize:12,color:"#6b7280"}}>{fmt(ganado)} / {fmt(meta)} · <strong style={{color:pct>=70?"#10b981":pct>=40?"#f59e0b":"#ef4444"}}>{pct}%</strong></span>
              </div>
              <ProgressBar value={ganado} max={meta} color={s.color} h={10}/>
            </div>
          );
        })}
      </Card>

      <Card>
        <h3 style={{margin:"0 0 14px",fontSize:14,fontWeight:700}}>📣 Inversión Redes Sociales</h3>
        <div style={{display:"flex",gap:12,flexWrap:"wrap"}}>
          {SOCIAL.map(ad=>{
            const cpl=Math.round(ad.inv/ad.leads);
            const cpa=Math.round(ad.inv/ad.conv);
            const roas=((ad.conv*25000)/ad.inv).toFixed(1);
            return (
              <div key={ad.p} style={{flex:1,minWidth:140,padding:"14px 16px",borderRadius:10,border:`2px solid ${ad.color}22`,background:`${ad.color}08`}}>
                <div style={{fontSize:13,fontWeight:800,color:ad.color,marginBottom:8}}>{ad.p}</div>
                {[["Inversión",fmt(ad.inv)],["Leads",ad.leads],["Conversiones",ad.conv],["CPL",fmt(cpl)],["CPA",fmt(cpa)],["ROAS",`${roas}x`]].map(([k,v])=>(
                  <div key={k} style={{display:"flex",justifyContent:"space-between",fontSize:11,color:"#6b7280",marginBottom:3}}>
                    <span>{k}</span><strong style={{color:"#111827"}}>{v}</strong>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

// ─────────────────────────────────────────────
// DASHBOARD VENDEDOR
// ─────────────────────────────────────────────
function DashboardVendedor({currentUser,contacts,eventos}) {
  const myC = contacts.filter(c=>c.vendedor_id===currentUser.id);
  const cerrados = myC.filter(c=>c.etapa==="Cerrado Ganado");
  const vendido = cerrados.reduce((s,c)=>s+c.valor,0);
  const comision = vendido*(currentUser.comision_pct/100);
  const metaComision = currentUser.meta*(currentUser.comision_pct/100);
  const myEvents = eventos.filter(e=>e.vendedor_id===currentUser.id);

  return (
    <div style={{display:"flex",flexDirection:"column",gap:20}}>
      <div style={{background:"linear-gradient(135deg,#ff7a59,#ff9a7b)",borderRadius:16,padding:"22px 26px",color:"#fff"}}>
        <div style={{display:"flex",alignItems:"center",gap:14}}>
          <Avatar initials={currentUser.avatar||currentUser.nombre.slice(0,2).toUpperCase()} size={50} color="rgba(255,255,255,.25)"/>
          <div>
            <div style={{fontSize:20,fontWeight:800}}>¡Hola, {currentUser.nombre.split(" ")[0]}! 👋</div>
            <div style={{fontSize:12,opacity:.85,marginTop:3}}>{new Date().toLocaleDateString("es-MX",{weekday:"long",day:"numeric",month:"long"})}</div>
          </div>
        </div>
      </div>

      <div style={{display:"flex",gap:14,flexWrap:"wrap"}}>
        {[
          {label:"Mis Leads",value:myC.length,color:"#0ea5e9"},
          {label:"Citas del Mes",value:myEvents.length,color:"#7c3aed"},
          {label:"Ventas Cerradas",value:cerrados.length,color:"#10b981"},
          {label:"Total Vendido",value:fmt(vendido),color:"#ff7a59"},
        ].map(s=>(
          <div key={s.label} style={{flex:1,minWidth:120,background:"#fff",borderRadius:12,padding:"16px 18px",border:"1px solid #f0f0f0",boxShadow:"0 1px 4px rgba(0,0,0,.06)"}}>
            <div style={{fontSize:11,color:"#6b7280",fontWeight:600,marginBottom:6}}>{s.label}</div>
            <div style={{fontSize:22,fontWeight:800,color:s.color}}>{s.value}</div>
          </div>
        ))}
      </div>

      <Card>
        <h3 style={{margin:"0 0 14px",fontSize:14,fontWeight:700}}>💵 Mis Comisiones del Mes</h3>
        <div style={{display:"flex",gap:20,alignItems:"center",flexWrap:"wrap"}}>
          <div style={{flex:1}}>
            <div style={{display:"flex",justifyContent:"space-between",marginBottom:7}}>
              <span style={{fontSize:13,color:"#6b7280"}}>Comisión ganada</span>
              <span style={{fontSize:14,fontWeight:800,color:"#10b981"}}>{fmt(comision)}</span>
            </div>
            <ProgressBar value={comision} max={metaComision||1} color="#10b981" h={12}/>
            <div style={{display:"flex",justifyContent:"space-between",marginTop:6}}>
              <span style={{fontSize:11,color:"#9ca3af"}}>Meta: {fmt(metaComision)}</span>
              <span style={{fontSize:11,color:"#9ca3af"}}>Falta: {fmt(Math.max(0,metaComision-comision))}</span>
            </div>
          </div>
          <div style={{textAlign:"center",padding:"14px 22px",background:"#f0fdf4",borderRadius:12,border:"1px solid #86efac"}}>
            <div style={{fontSize:28,fontWeight:900,color:"#166534"}}>{metaComision?Math.round((comision/metaComision)*100):0}%</div>
            <div style={{fontSize:11,color:"#166534",fontWeight:600}}>de tu meta</div>
            <div style={{fontSize:10,color:"#4ade80",marginTop:2}}>{currentUser.comision_pct}% por venta</div>
          </div>
        </div>
      </Card>

      <Card>
        <h3 style={{margin:"0 0 12px",fontSize:14,fontWeight:700}}>📅 Próximas Citas</h3>
        {myEvents.length===0?<p style={{color:"#9ca3af",fontSize:13}}>Sin citas agendadas</p>:myEvents.slice(0,4).map(ev=>(
          <div key={ev.id} style={{display:"flex",gap:12,alignItems:"center",padding:"10px 0",borderBottom:"1px solid #f9fafb"}}>
            <div style={{background:"#fff3f0",padding:"6px 10px",borderRadius:8,textAlign:"center",minWidth:44}}>
              <div style={{fontSize:13,fontWeight:800,color:"#ff7a59"}}>{ev.fecha?.slice(8)}</div>
              <div style={{fontSize:9,color:"#ff7a59"}}>{ev.hora?.slice(0,5)}</div>
            </div>
            <div>
              <div style={{fontSize:13,fontWeight:700,color:"#111827"}}>{ev.titulo}</div>
              <div style={{fontSize:11,color:"#9ca3af"}}>{ev.tipo==="demo"?"🖥️ Demo":ev.tipo==="cierre"?"🤝 Cierre":"📋 Cita"}</div>
            </div>
          </div>
        ))}
      </Card>
    </div>
  );
}

// ─────────────────────────────────────────────
            
