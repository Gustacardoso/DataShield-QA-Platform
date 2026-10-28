import { ProcessamentoColunasPage } from "../components/ProcessamentoColunasPage";

export function Anonimizacao() {
  return (
    <ProcessamentoColunasPage
      titulo="Anonimização"
      rota="anonimizacao"
      campoColunas="colunas_anonimizadas"
      textos={{
        botaoAcao: "Anonimizar",
        instrucao:
          'Selecione as colunas que devem ser anonimizadas (as sensíveis já vêm marcadas). O valor original é removido em definitivo e vira "ANONIMO".',
        botaoAplicar: "Aplicar anonimização",
        erroAplicar: "Não foi possível aplicar a anonimização.",
        resumo: (qtd, colunas) => `${qtd} coluna(s) anonimizada(s): ${colunas}`,
        download: "Baixar arquivo anonimizado",
      }}
    />
  );
}
