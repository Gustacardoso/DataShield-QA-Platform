import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogContent,
  DialogTitle,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

type ArquivoImportado = {
  id: number;
  nome_arquivo: string;
  formato: string;
  num_linhas: number;
  colunas: string[];
  criado_em: string;
};

type DadoEncontrado = {
  coluna: string;
  tipo_dado: string | null;
  quantidade_encontrada: number;
  tratado: boolean;
};

type AvaliacaoLgpd = {
  arquivo_id: number;
  nome_arquivo: string;
  nivel_risco: string;
  total_colunas_sensiveis: number;
  colunas_tratadas: number;
  dados_encontrados: DadoEncontrado[];
};

const COR_RISCO: Record<string, "error" | "warning" | "success" | "default"> = {
  Alto: "error",
  Médio: "warning",
  Baixo: "success",
};

export function Lgpd() {
  const [arquivos, setArquivos] = useState<ArquivoImportado[]>([]);
  const [erroListagem, setErroListagem] = useState<string | null>(null);
  const [avaliandoId, setAvaliandoId] = useState<number | null>(null);
  const [erroAvaliacao, setErroAvaliacao] = useState<string | null>(null);
  const [resultado, setResultado] = useState<AvaliacaoLgpd | null>(null);

  useEffect(() => {
    apiClient
      .get<ArquivoImportado[]>("/api/importacao/")
      .then((response) => setArquivos(response.data))
      .catch(() => setErroListagem("Não foi possível carregar os arquivos importados."));
  }, []);

  const avaliar = (id: number) => {
    setAvaliandoId(id);
    setErroAvaliacao(null);
    apiClient
      .get<AvaliacaoLgpd>(`/api/lgpd/${id}`)
      .then((response) => setResultado(response.data))
      .catch(() => setErroAvaliacao("Não foi possível avaliar este arquivo."))
      .finally(() => setAvaliandoId(null));
  };

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Avaliação LGPD
      </Typography>

      {erroAvaliacao && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {erroAvaliacao}
        </Alert>
      )}
      {erroListagem && <Alert severity="error">{erroListagem}</Alert>}

      {!erroListagem && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nome</TableCell>
                <TableCell>Formato</TableCell>
                <TableCell align="right">Linhas</TableCell>
                <TableCell align="right">Colunas</TableCell>
                <TableCell align="right">Ação</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {arquivos.map((arquivo) => (
                <TableRow key={arquivo.id} hover>
                  <TableCell>{arquivo.nome_arquivo}</TableCell>
                  <TableCell>{arquivo.formato}</TableCell>
                  <TableCell align="right">{arquivo.num_linhas}</TableCell>
                  <TableCell align="right">{arquivo.colunas.length}</TableCell>
                  <TableCell align="right">
                    <Button size="small" variant="contained" disabled={avaliandoId === arquivo.id} onClick={() => avaliar(arquivo.id)}>
                      {avaliandoId === arquivo.id ? "Avaliando..." : "Avaliar"}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {arquivos.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    Nenhum arquivo importado ainda. Importe um arquivo primeiro.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={resultado !== null} onClose={() => setResultado(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{resultado?.nome_arquivo}</DialogTitle>
        <DialogContent>
          {resultado && (
            <>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
                <Typography variant="body1">Nível de risco:</Typography>
                <Chip label={resultado.nivel_risco} color={COR_RISCO[resultado.nivel_risco] ?? "default"} />
                <Typography variant="body2" color="text.secondary">
                  {resultado.colunas_tratadas}/{resultado.total_colunas_sensiveis} colunas sensíveis já tratadas
                </Typography>
              </Box>

              {resultado.dados_encontrados.length === 0 ? (
                <Alert severity="success">Nenhum dado sensível encontrado neste arquivo.</Alert>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Coluna</TableCell>
                        <TableCell>Tipo</TableCell>
                        <TableCell align="right">Encontrados</TableCell>
                        <TableCell align="center">Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {resultado.dados_encontrados.map((dado) => (
                        <TableRow key={dado.coluna}>
                          <TableCell>{dado.coluna}</TableCell>
                          <TableCell>{dado.tipo_dado ?? "—"}</TableCell>
                          <TableCell align="right">{dado.quantidade_encontrada}</TableCell>
                          <TableCell align="center">
                            {dado.tratado ? (
                              <CheckCircleIcon fontSize="small" color="success" titleAccess="Tratado" />
                            ) : (
                              <WarningAmberIcon fontSize="small" color="warning" titleAccess="Não tratado" />
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
