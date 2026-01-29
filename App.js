import React, { useState, useEffect } from "react";
import DoctorDashboard from "./components/DoctorDashboard";
import PatientHistory from "./components/PatientHistory";
import AudioRecorder from "./components/AudioRecorder";

function App() {
  const [patients, setPatients] = useState(() => {
    const saved = localStorage.getItem("patients");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem("patients", JSON.stringify(patients));
  }, [patients]);

  const addPatient = (patient) => {
    setPatients([...patients, patient]);
  };

  const deletePatient = (index) => {
    const updated = patients.filter((_, i) => i !== index);
    setPatients(updated);
  };

  const clearPatients = () => {
    setPatients([]);
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif", backgroundColor: "#f5f5f5", minHeight: "100vh" }}>
      <h1 style={{ textAlign: "center", padding: "20px", color: "#1976d2" }}>
        🏥 Medical Clinic Analysis App
      </h1>
      <DoctorDashboard addPatient={addPatient} />
      <PatientHistory
        patients={patients}
        deletePatient={deletePatient}
        clearPatients={clearPatients}
      />
      <AudioRecorder />
    </div>
  );
}

export default App;
