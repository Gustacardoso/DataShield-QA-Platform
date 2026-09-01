import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Anonimizacao } from "./pages/Anonimizacao";
import { Dashboard } from "./pages/Dashboard";
import { Descoberta } from "./pages/Descoberta";
import { Importacao } from "./pages/Importacao";
import { Lgpd } from "./pages/Lgpd";
import { Mascaramento } from "./pages/Mascaramento";
import { Sinteticos } from "./pages/Sinteticos";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/importacao" element={<Importacao />} />
        <Route path="/descoberta" element={<Descoberta />} />
        <Route path="/mascaramento" element={<Mascaramento />} />
        <Route path="/anonimizacao" element={<Anonimizacao />} />
        <Route path="/sinteticos" element={<Sinteticos />} />
        <Route path="/lgpd" element={<Lgpd />} />
      </Routes>
    </Layout>
  );
}

export default App;
