import {
  Alert,
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

type ColunaClassificada = {
  nome_coluna: string;
  sensivel: boolean;
  tipo_dado: string | null;
};

type DescobertaResultado = {
  arquivo_id: number;
  nome_arquivo: string;
  colunas: ColunaClassificada[];
};

export function Descoberta() {
  const [arquivos, setArquivos] = useState<ArquivoImportado[]>([]);
  const [erroListagem, setErroListagem] = useState<string | null>(null);
  const [analisadoIds, setAnalisadoIds] = useState<Set<number>>(new Set());
  const [analisandoId, setAnalisandoId] = useState<number | null>(null);
  const [resultado, setResultado] = useState<DescobertaResultado | null>(null);
  const [erroAnalise, setErroAnalise] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<ArquivoImportado[]>("/api/importacao/")
      .then((response) => setArquivos(response.data))
      .catch(() => setErroListagem("Não foi possível carregar os arquivos importados."));
  }, []);

  const analisar = (id: number) => {
    setAnalisandoId(id);
    setErroAnalise(null);
    apiClient
      .post<DescobertaResultado>(`/api/descoberta/${id}/analisar`)
      .then((response) => {
        setAnalisadoIds((atual) => new Set(atual).add(id));
        setResultado(response.data);
      })
      .catch(() => setErroAnalise("Não foi possível analisar este arquivo."))
      .finally(() => setAnalisandoId(null));
  };

  const verResultado = (id: number) => {
    apiClient.get<DescobertaResultado>(`/api/descoberta/${id}`).then((response) => setResultado(response.data));
  };

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Descoberta de Dados Sensíveis
      </Typography>

      {erroAnalise && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {erroAnalise}
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
              {arquivos.map((arquivo) => {
                const jaAnalisado = analisadoIds.has(arquivo.id);
                return (
                  <TableRow key={arquivo.id} hover>
                    <TableCell>{arquivo.nome_arquivo}</TableCell>
                    <TableCell>{arquivo.formato}</TableCell>
                    <TableCell align="right">{arquivo.num_linhas}</TableCell>
                    <TableCell align="right">{arquivo.colunas.length}</TableCell>
                    <TableCell align="right">
                      <Button
                        size="small"
                        variant={jaAnalisado ? "outlined" : "contained"}
                        disabled={analisandoId === arquivo.id}
                        onClick={() => (jaAnalisado ? verResultado(arquivo.id) : analisar(arquivo.id))}
                      >
                        {analisandoId === arquivo.id
                          ? "Analisando..."
                          : jaAnalisado
                            ? "Ver resultado"
                            : "Analisar"}
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
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
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Coluna</TableCell>
                    <TableCell>Classificação</TableCell>
                    <TableCell>Tipo detectado</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {resultado.colunas.map((coluna) => (
                    <TableRow key={coluna.nome_coluna}>
                      <TableCell>{coluna.nome_coluna}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={coluna.sensivel ? "Sensível" : "Não sensível"}
                          color={coluna.sensivel ? "error" : "default"}
                          variant={coluna.sensivel ? "filled" : "outlined"}
                        />
                      </TableCell>
                      <TableCell>{coluna.tipo_dado ?? "—"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
