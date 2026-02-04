import React from "react";
import { Card, CardContent, Typography } from "@mui/material";

function StylishCard({ title, children }) {
  return (
    <Card
      sx={{
        transition: "0.3s ease",
        borderRadius: 3,
        boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
        "&:hover": {
          transform: "scale(1.05)",
          boxShadow: "0 12px 35px rgba(0,0,0,0.25)",
        },
      }}
    >
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        {children}
      </CardContent>
    </Card>
  );
}

export default StylishCard;
