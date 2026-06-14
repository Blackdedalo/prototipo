import React from "react";
import { FileText, Home, ListChecks, Search } from "lucide-react";
import { useEffect, useState } from "react";

import AdminDashboard from "./pages/AdminDashboard.jsx";
import ComplaintWizard from "./pages/ComplaintWizard.jsx";
import HomeChat from "./pages/HomeChat.jsx";
import Tracking from "./pages/Tracking.jsx";

const routes = {
  "/": HomeChat,
  "/denuncia": ComplaintWizard,
  "/seguimiento": Tracking,
  "/admin": AdminDashboard,
};

function currentPath() {
  return window.location.pathname in routes ? window.location.pathname : "/";
}

export default function App() {
  const [path, setPath] = useState(currentPath());

  useEffect(() => {
    const onPop = () => setPath(currentPath());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const navigate = (nextPath) => {
    window.history.pushState({}, "", nextPath);
    setPath(nextPath);
  };

  const Page = routes[path] || HomeChat;

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => navigate("/")}>
          <span className="brand-mark">PNP</span>
          <span>Denuncia Virtual</span>
        </button>
        <nav>
          <button className={path === "/" ? "active" : ""} onClick={() => navigate("/")}>
            <Home size={18} /> Inicio
          </button>
          <button className={path === "/denuncia" ? "active" : ""} onClick={() => navigate("/denuncia")}>
            <FileText size={18} /> Denuncia
          </button>
          <button className={path === "/seguimiento" ? "active" : ""} onClick={() => navigate("/seguimiento")}>
            <Search size={18} /> Seguimiento
          </button>
          <button className={path === "/admin" ? "active" : ""} onClick={() => navigate("/admin")}>
            <ListChecks size={18} /> Admin
          </button>
        </nav>
      </header>
      <main>
        <Page navigate={navigate} />
      </main>
    </div>
  );
}
