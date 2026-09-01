import DeleteIcon from "@mui/icons-material/Delete";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
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
  const [selecionados, setSelecionados] = useState<number[]>([]);
  const [confirmandoExclusao, setConfirmandoExclusao] = useState(false);
  const [excluindo, setExcluindo] = useState(false);

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

  const alternarSelecao = (id: number) => {
    setSelecionados((atual) => (atual.includes(id) ? atual.filter((item) => item !== id) : [...atual, id]));
  };

  const alternarSelecaoTodos = () => {
    setSelecionados((atual) => (atual.length === arquivos.length ? [] : arquivos.map((arquivo) => arquivo.id)));
  };

  const excluirSelecionados = () => {
    setExcluindo(true);
    apiClient
      .delete("/api/importacao/", { data: { ids: selecionados } })
      .then(() => {
        setSelecionados([]);
        carregarArquivos();
      })
      .finally(() => {
        setExcluindo(false);
        setConfirmandoExclusao(false);
      });
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
        <>
          <Box sx={{ mb: 1, display: "flex", justifyContent: "flex-end" }}>
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              disabled={selecionados.length === 0}
              onClick={() => setConfirmandoExclusao(true)}
            >
              Excluir selecionados ({selecionados.length})
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={arquivos.length > 0 && selecionados.length === arquivos.length}
                      indeterminate={selecionados.length > 0 && selecionados.length < arquivos.length}
                      onChange={alternarSelecaoTodos}
                    />
                  </TableCell>
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
                    <TableCell padding="checkbox" onClick={(e) => e.stopPropagation()}>
                      <Checkbox
                        checked={selecionados.includes(arquivo.id)}
                        onChange={() => alternarSelecao(arquivo.id)}
                      />
                    </TableCell>
                    <TableCell>{arquivo.nome_arquivo}</TableCell>
                    <TableCell>{arquivo.formato}</TableCell>
                    <TableCell align="right">{arquivo.num_linhas}</TableCell>
                    <TableCell align="right">{arquivo.colunas.length}</TableCell>
                    <TableCell>{new Date(arquivo.criado_em).toLocaleString("pt-BR")}</TableCell>
                  </TableRow>
                ))}
                {arquivos.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      Nenhum arquivo importado ainda.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </>
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

      <Dialog open={confirmandoExclusao} onClose={() => setConfirmandoExclusao(false)}>
        <DialogTitle>Excluir arquivos</DialogTitle>
        <DialogContent>
          Tem certeza que deseja excluir {selecionados.length} arquivo(s) importado(s)? Essa ação não pode ser
          desfeita.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmandoExclusao(false)} disabled={excluindo}>
            Cancelar
          </Button>
          <Button color="error" variant="contained" onClick={excluirSelecionados} disabled={excluindo}>
            {excluindo ? "Excluindo..." : "Excluir"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
