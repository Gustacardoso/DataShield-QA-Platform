import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import DashboardIcon from "@mui/icons-material/Dashboard";
import GavelIcon from "@mui/icons-material/Gavel";
import PersonOffIcon from "@mui/icons-material/PersonOff";
import SearchIcon from "@mui/icons-material/Search";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import type { SvgIconComponent } from "@mui/icons-material";

export type NavItem = {
  path: string;
  label: string;
  icon: SvgIconComponent;
};

export const navItems: NavItem[] = [
  { path: "/", label: "Dashboard", icon: DashboardIcon },
  { path: "/importacao", label: "Importação", icon: UploadFileIcon },
  { path: "/descoberta", label: "Descoberta de Dados", icon: SearchIcon },
  { path: "/mascaramento", label: "Mascaramento", icon: VisibilityOffIcon },
  { path: "/anonimizacao", label: "Anonimização", icon: PersonOffIcon },
  { path: "/sinteticos", label: "Dados Sintéticos", icon: AutoAwesomeIcon },
  { path: "/lgpd", label: "Avaliação LGPD", icon: GavelIcon },
];
