import React, { useState } from "react";
import { Box, TextField, Button, Typography, Paper } from "@mui/material";

function DoctorDashboard({ addPatient }) {
  const [patient, setPatient] = useState({ name: "", age: "", gender: "" });

  const handleSubmit = () => {
    if (patient.name && patient.age && patient.gender) {
      addPatient(patient); // send patient to App.js
      setPatient({ name: "", age: "", gender: "" }); // clear form
    } else {
      alert("Please fill all fields!");
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, m: 3 }}>
      <Typography variant="h4" gutterBottom color="primary">
        Doctor Dashboard
      </Typography>
      <Box display="flex" flexDirection="column" gap={2}>
        <TextField
          label="Patient Name"
          variant="outlined"
          value={patient.name}
          onChange={(e) => setPatient({ ...patient, name: e.target.value })}
        />
        <TextField
          label="Age"
          type="number"
          variant="outlined"
          value={patient.age}
          onChange={(e) => setPatient({ ...patient, age: e.target.value })}
        />
        <TextField
          label="Gender"
          variant="outlined"
          value={patient.gender}
          onChange={(e) => setPatient({ ...patient, gender: e.target.value })}
        />
        <Button variant="contained" color="primary" onClick={handleSubmit}>
          Register Patient
        </Button>
      </Box>
    </Paper>
  );
}

export default DoctorDashboard;
