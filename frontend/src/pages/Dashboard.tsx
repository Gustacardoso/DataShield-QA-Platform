import { Alert, Card, CardContent, CircularProgress, Grid, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

type DashboardSummary = {
  arquivos_processados: number;
  dados_mascarados: number;
  dados_anonimizados: number;
  dados_sinteticos_gerados: number;
  indice_conformidade_lgpd: number;
};

const INDICATORS: { key: keyof DashboardSummary; label: string }[] = [
  { key: "arquivos_processados", label: "Arquivos Processados" },
  { key: "dados_mascarados", label: "Dados Mascarados" },
  { key: "dados_anonimizados", label: "Dados Anonimizados" },
  { key: "dados_sinteticos_gerados", label: "Dados Sintéticos Gerados" },
  { key: "indice_conformidade_lgpd", label: "Índice de Conformidade LGPD" },
];

export function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<DashboardSummary>("/api/dashboard/summary")
      .then((response) => setSummary(response.data))
      .catch(() => setError("Não foi possível carregar os indicadores. Verifique se a API está rodando."));
  }, []);

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}
      {!error && !summary && <CircularProgress />}

      {summary && (
        <Grid container spacing={2}>
          {INDICATORS.map(({ key, label }) => (
            <Grid key={key} size={{ xs: 12, sm: 6, md: 4 }}>
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
        </Grid>
      )}
    </>
  );
}
