import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function PatientSearch() {
  const [patientId, setPatientId] = useState("");
  const navigate = useNavigate();

  return (
    <div>
      <h3>Search Patient</h3>

      <input
        placeholder="Patient ID"
        onChange={(e) => setPatientId(e.target.value)}
      />

      <button onClick={() => navigate(`/doctor/patient/${patientId}`)}>
        Search
      </button>
    </div>
  );
}
