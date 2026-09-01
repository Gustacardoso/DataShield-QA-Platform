import { Alert, Typography } from "@mui/material";

export function ModulePlaceholder({ title }: { title: string }) {
  return (
    <>
      <Typography variant="h4" gutterBottom>
        {title}
      </Typography>
      <Alert severity="info">Módulo em construção.</Alert>
    </>
  );
}
