import {
  Alert,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Link,
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

type AnonimizacaoResultado = {
  arquivo_id: number;
  nome_arquivo: string;
  colunas_anonimizadas: string[];
  preview: Record<string, unknown>[];
};

export function Anonimizacao() {
  const [arquivos, setArquivos] = useState<ArquivoImportado[]>([]);
  const [erroListagem, setErroListagem] = useState<string | null>(null);
  const [anonimizadoIds, setAnonimizadoIds] = useState<Set<number>>(new Set());

  const [dialogArquivo, setDialogArquivo] = useState<DescobertaResultado | null>(null);
  const [colunasSelecionadas, setColunasSelecionadas] = useState<Set<string>>(new Set());
  const [carregandoColunas, setCarregandoColunas] = useState(false);
  const [erroDialog, setErroDialog] = useState<string | null>(null);
  const [aplicando, setAplicando] = useState(false);
  const [resultado, setResultado] = useState<AnonimizacaoResultado | null>(null);

  useEffect(() => {
    apiClient
      .get<ArquivoImportado[]>("/api/importacao/")
      .then((response) => setArquivos(response.data))
      .catch(() => setErroListagem("Não foi possível carregar os arquivos importados."));
  }, []);

  const abrirSelecaoColunas = (arquivo: ArquivoImportado) => {
    setResultado(null);
    setErroDialog(null);
    setCarregandoColunas(true);
    setDialogArquivo({ arquivo_id: arquivo.id, nome_arquivo: arquivo.nome_arquivo, colunas: [] });

    apiClient
      .get<DescobertaResultado>(`/api/descoberta/${arquivo.id}`)
      .catch(() => apiClient.post<DescobertaResultado>(`/api/descoberta/${arquivo.id}/analisar`))
      .then((response) => {
        setDialogArquivo(response.data);
        setColunasSelecionadas(new Set(response.data.colunas.filter((c) => c.sensivel).map((c) => c.nome_coluna)));
      })
      .catch(() => setErroDialog("Não foi possível analisar as colunas deste arquivo."))
      .finally(() => setCarregandoColunas(false));
  };

  const alternarColuna = (nomeColuna: string) => {
    setColunasSelecionadas((atual) => {
      const proximo = new Set(atual);
      if (proximo.has(nomeColuna)) {
        proximo.delete(nomeColuna);
      } else {
        proximo.add(nomeColuna);
      }
      return proximo;
    });
  };

  const aplicarAnonimizacao = () => {
    if (!dialogArquivo) return;

    setAplicando(true);
    setErroDialog(null);
    apiClient
      .post<AnonimizacaoResultado>(`/api/anonimizacao/${dialogArquivo.arquivo_id}/aplicar`, {
        colunas: Array.from(colunasSelecionadas),
      })
      .then((response) => {
        setResultado(response.data);
        setAnonimizadoIds((atual) => new Set(atual).add(dialogArquivo.arquivo_id));
      })
      .catch(() => setErroDialog("Não foi possível aplicar a anonimização."))
      .finally(() => setAplicando(false));
  };

  const fecharDialog = () => {
    setDialogArquivo(null);
    setResultado(null);
  };

  const urlDownload = dialogArquivo
    ? `${apiClient.defaults.baseURL}/api/anonimizacao/${dialogArquivo.arquivo_id}/download`
    : "";

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Anonimização
      </Typography>

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
                    <Button
                      size="small"
                      variant={anonimizadoIds.has(arquivo.id) ? "outlined" : "contained"}
                      onClick={() => abrirSelecaoColunas(arquivo)}
                    >
                      {anonimizadoIds.has(arquivo.id) ? "Ver resultado" : "Anonimizar"}
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

      <Dialog open={dialogArquivo !== null} onClose={fecharDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{dialogArquivo?.nome_arquivo}</DialogTitle>
        <DialogContent>
          {carregandoColunas && <CircularProgress />}
          {erroDialog && <Alert severity="error">{erroDialog}</Alert>}

          {!carregandoColunas && !resultado && dialogArquivo && dialogArquivo.colunas.length > 0 && (
            <>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Selecione as colunas que devem ser anonimizadas (as sensíveis já vêm marcadas). O valor original é
                removido em definitivo e vira "ANONIMO".
              </Typography>
              {dialogArquivo.colunas.map((coluna) => (
                <FormControlLabel
                  key={coluna.nome_coluna}
                  sx={{ display: "flex" }}
                  control={
                    <Checkbox
                      checked={colunasSelecionadas.has(coluna.nome_coluna)}
                      onChange={() => alternarColuna(coluna.nome_coluna)}
                    />
                  }
                  label={
                    <>
                      {coluna.nome_coluna}
                      {coluna.tipo_dado && (
                        <Chip size="small" label={coluna.tipo_dado} sx={{ ml: 1 }} variant="outlined" />
                      )}
                    </>
                  }
                />
              ))}
            </>
          )}

          {resultado && (
            <>
              <Alert severity="success" sx={{ mb: 2 }}>
                {resultado.colunas_anonimizadas.length} coluna(s) anonimizada(s):{" "}
                {resultado.colunas_anonimizadas.join(", ") || "nenhuma"}
              </Alert>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {Object.keys(resultado.preview[0] ?? {}).map((coluna) => (
                        <TableCell key={coluna}>{coluna}</TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {resultado.preview.map((linha, index) => (
                      <TableRow key={index}>
                        {Object.keys(resultado.preview[0] ?? {}).map((coluna) => (
                          <TableCell key={coluna}>{String(linha[coluna] ?? "")}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <Link href={urlDownload} sx={{ mt: 2, display: "inline-block" }}>
                Baixar arquivo anonimizado
              </Link>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={fecharDialog}>Fechar</Button>
          {!resultado && (
            <Button
              variant="contained"
              disabled={carregandoColunas || aplicando || colunasSelecionadas.size === 0}
              onClick={aplicarAnonimizacao}
            >
              {aplicando ? "Aplicando..." : "Aplicar anonimização"}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
}
