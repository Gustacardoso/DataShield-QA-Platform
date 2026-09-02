import {
  Alert,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Link,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
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

type SinteticosResultado = {
  arquivo_id: number;
  nome_arquivo: string;
  num_linhas: number;
  preview: Record<string, unknown>[];
};

export function Sinteticos() {
  const [arquivos, setArquivos] = useState<ArquivoImportado[]>([]);
  const [erroListagem, setErroListagem] = useState<string | null>(null);
  const [geradoIds, setGeradoIds] = useState<Set<number>>(new Set());

  const [dialogArquivo, setDialogArquivo] = useState<ArquivoImportado | null>(null);
  const [numLinhas, setNumLinhas] = useState(100);
  const [gerando, setGerando] = useState(false);
  const [erroDialog, setErroDialog] = useState<string | null>(null);
  const [resultado, setResultado] = useState<SinteticosResultado | null>(null);

  useEffect(() => {
    apiClient
      .get<ArquivoImportado[]>("/api/importacao/")
      .then((response) => setArquivos(response.data))
      .catch(() => setErroListagem("Não foi possível carregar os arquivos importados."));
  }, []);

  const abrirDialog = (arquivo: ArquivoImportado) => {
    setResultado(null);
    setErroDialog(null);
    setNumLinhas(100);
    setDialogArquivo(arquivo);
  };

  const gerar = () => {
    if (!dialogArquivo) return;

    setGerando(true);
    setErroDialog(null);
    apiClient
      .post<SinteticosResultado>(`/api/sinteticos/${dialogArquivo.id}/gerar`, { num_linhas: numLinhas })
      .then((response) => {
        setResultado(response.data);
        setGeradoIds((atual) => new Set(atual).add(dialogArquivo.id));
      })
      .catch((error) => {
        const mensagem = error.response?.data?.detail ?? "Não foi possível gerar os dados sintéticos.";
        setErroDialog(typeof mensagem === "string" ? mensagem : "Não foi possível gerar os dados sintéticos.");
      })
      .finally(() => setGerando(false));
  };

  const fecharDialog = () => {
    setDialogArquivo(null);
    setResultado(null);
  };

  const urlDownload = dialogArquivo ? `${apiClient.defaults.baseURL}/api/sinteticos/${dialogArquivo.id}/download` : "";

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Dados Sintéticos
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
                      variant={geradoIds.has(arquivo.id) ? "outlined" : "contained"}
                      onClick={() => abrirDialog(arquivo)}
                    >
                      {geradoIds.has(arquivo.id) ? "Ver resultado" : "Gerar"}
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
          {erroDialog && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {erroDialog}
            </Alert>
          )}

          {!resultado && (
            <>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Gera linhas totalmente fictícias com a mesma estrutura de colunas deste arquivo — nenhum valor real é
                usado.
              </Typography>
              <TextField
                label="Quantidade de linhas"
                type="number"
                size="small"
                value={numLinhas}
                onChange={(e) => setNumLinhas(Number(e.target.value))}
                slotProps={{ htmlInput: { min: 1, max: 50_000 } }}
              />
            </>
          )}

          {gerando && (
            <Typography sx={{ mt: 2 }}>
              <CircularProgress size={16} sx={{ mr: 1, verticalAlign: "middle" }} />
              Gerando...
            </Typography>
          )}

          {resultado && (
            <>
              <Alert severity="success" sx={{ mb: 2 }}>
                {resultado.num_linhas} linha(s) sintética(s) geradas.
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
                Baixar arquivo sintético
              </Link>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={fecharDialog}>Fechar</Button>
          {!resultado && (
            <Button
              variant="contained"
              disabled={gerando || numLinhas < 1 || numLinhas > 50_000}
              onClick={gerar}
            >
              {gerando ? "Gerando..." : "Gerar"}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
}
