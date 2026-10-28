import { ProcessamentoColunasPage } from "../components/ProcessamentoColunasPage";

export function Mascaramento() {
  return (
    <ProcessamentoColunasPage
      titulo="Mascaramento"
      rota="mascaramento"
      campoColunas="colunas_mascaradas"
      textos={{
        botaoAcao: "Mascarar",
        instrucao: "Selecione as colunas que devem ser mascaradas (as sensíveis já vêm marcadas).",
        botaoAplicar: "Aplicar mascaramento",
        erroAplicar: "Não foi possível aplicar o mascaramento.",
        resumo: (qtd, colunas) => `${qtd} coluna(s) mascarada(s): ${colunas}`,
        download: "Baixar arquivo mascarado",
      }}
    />
  );
}
