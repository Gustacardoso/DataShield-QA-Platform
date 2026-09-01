import {
  Alert,
  Button,
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

type ArquivoImportadoDetalhe = ArquivoImportado & {
  preview: Record<string, unknown>[];
};

export function Importacao() {
  const [arquivos, setArquivos] = useState<ArquivoImportado[]>([]);
  const [erroListagem, setErroListagem] = useState<string | null>(null);
  const [arquivoSelecionado, setArquivoSelecionado] = useState<File | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [erroUpload, setErroUpload] = useState<string | null>(null);
  const [detalhe, setDetalhe] = useState<ArquivoImportadoDetalhe | null>(null);

  const carregarArquivos = () => {
    apiClient
      .get<ArquivoImportado[]>("/api/importacao/")
      .then((response) => setArquivos(response.data))
      .catch(() => setErroListagem("Não foi possível carregar os arquivos importados."));
  };

  useEffect(carregarArquivos, []);

  const enviarArquivo = () => {
    if (!arquivoSelecionado) return;

    const formData = new FormData();
    formData.append("arquivo", arquivoSelecionado);

    setEnviando(true);
    setErroUpload(null);
    apiClient
      .post("/api/importacao/upload", formData)
      .then(() => {
        setArquivoSelecionado(null);
        carregarArquivos();
      })
      .catch((error) => {
        const mensagem = error.response?.data?.detail ?? "Falha ao enviar o arquivo.";
        setErroUpload(mensagem);
      })
      .finally(() => setEnviando(false));
  };

  const abrirDetalhe = (id: number) => {
    apiClient.get<ArquivoImportadoDetalhe>(`/api/importacao/${id}`).then((response) => setDetalhe(response.data));
  };

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Importação de Dados
      </Typography>

      <Paper sx={{ p: 2, mb: 3, display: "flex", alignItems: "center", gap: 2 }}>
        <Button variant="outlined" component="label">
          Selecionar arquivo
          <input
            type="file"
            hidden
            accept=".csv,.txt,.xlsx,.xls,.json"
            onChange={(e) => setArquivoSelecionado(e.target.files?.[0] ?? null)}
          />
        </Button>
        <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
          {arquivoSelecionado ? arquivoSelecionado.name : "Nenhum arquivo selecionado"}
        </Typography>
        <Button variant="contained" disabled={!arquivoSelecionado || enviando} onClick={enviarArquivo}>
          {enviando ? "Enviando..." : "Enviar"}
        </Button>
      </Paper>

      {erroUpload && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {erroUpload}
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
                <TableCell>Importado em</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {arquivos.map((arquivo) => (
                <TableRow key={arquivo.id} hover sx={{ cursor: "pointer" }} onClick={() => abrirDetalhe(arquivo.id)}>
                  <TableCell>{arquivo.nome_arquivo}</TableCell>
                  <TableCell>{arquivo.formato}</TableCell>
                  <TableCell align="right">{arquivo.num_linhas}</TableCell>
                  <TableCell align="right">{arquivo.colunas.length}</TableCell>
                  <TableCell>{new Date(arquivo.criado_em).toLocaleString("pt-BR")}</TableCell>
                </TableRow>
              ))}
              {arquivos.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    Nenhum arquivo importado ainda.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={detalhe !== null} onClose={() => setDetalhe(null)} maxWidth="md" fullWidth>
        <DialogTitle>{detalhe?.nome_arquivo}</DialogTitle>
        <DialogContent>
          {detalhe && (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    {detalhe.colunas.map((coluna) => (
                      <TableCell key={coluna}>{coluna}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {detalhe.preview.map((linha, index) => (
                    <TableRow key={index}>
                      {detalhe.colunas.map((coluna) => (
                        <TableCell key={coluna}>{String(linha[coluna] ?? "")}</TableCell>
                      ))}
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
