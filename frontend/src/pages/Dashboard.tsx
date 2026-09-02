import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import { Alert, Box, Card, CardContent, CircularProgress, Grid, LinearProgress, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

type DashboardSummary = {
  arquivos_processados: number;
  dados_mascarados: number;
  dados_anonimizados: number;
  dados_sinteticos_gerados: number;
  indice_conformidade_lgpd: number;
};

const INDICADORES: { key: keyof DashboardSummary; label: string }[] = [
  { key: "arquivos_processados", label: "Arquivos processados" },
  { key: "dados_mascarados", label: "Dados mascarados" },
  { key: "dados_anonimizados", label: "Dados anonimizados" },
  { key: "dados_sinteticos_gerados", label: "Dados sintéticos gerados" },
];

// Cores de status fixas (nunca usadas como identidade de série) — o ícone +
// rótulo sempre acompanham a cor, ela nunca carrega o significado sozinha.
const STATUS_CONFORMIDADE = {
  alta: { cor: "#0ca30c", trilha: "#cdeecd", Icone: CheckCircleIcon, texto: "Conformidade alta" },
  parcial: { cor: "#fab219", trilha: "#fdecc8", Icone: WarningAmberIcon, texto: "Conformidade parcial" },
  baixa: { cor: "#d03b3b", trilha: "#f6d4d4", Icone: ErrorIcon, texto: "Conformidade baixa" },
} as const;

function statusConformidade(indice: number) {
  if (indice >= 80) return STATUS_CONFORMIDADE.alta;
  if (indice >= 50) return STATUS_CONFORMIDADE.parcial;
  return STATUS_CONFORMIDADE.baixa;
}

export function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<DashboardSummary>("/api/dashboard/summary")
      .then((response) => setSummary(response.data))
      .catch(() => setError("Não foi possível carregar os indicadores. Verifique se a API está rodando."));
  }, []);

  const status = summary ? statusConformidade(summary.indice_conformidade_lgpd) : null;

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}
      {!error && !summary && <CircularProgress />}

      {summary && status && (
        <Grid container spacing={2}>
          {INDICADORES.map(({ key, label }) => (
            <Grid key={key} size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    {label}
                  </Typography>
                  <Typography variant="h4">{summary[key]}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}

          <Grid size={12}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Índice de conformidade LGPD
                </Typography>
                <Box sx={{ display: "flex", alignItems: "baseline", gap: 2, mb: 1.5 }}>
                  <Typography variant="h3">{summary.indice_conformidade_lgpd}%</Typography>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                    <status.Icone fontSize="small" sx={{ color: status.cor }} />
                    <Typography variant="body2" color="text.secondary">
                      {status.texto}
                    </Typography>
                  </Box>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={summary.indice_conformidade_lgpd}
                  sx={{
                    height: 10,
                    borderRadius: 5,
                    backgroundColor: status.trilha,
                    "& .MuiLinearProgress-bar": { backgroundColor: status.cor, borderRadius: 5 },
                  }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: "block" }}>
                  Percentual de colunas sensíveis já mascaradas ou anonimizadas, considerando todos os arquivos
                  importados.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </>
  );
}
