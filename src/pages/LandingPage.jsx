import { useNavigate } from "react-router-dom";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div style={{ textAlign: "center", marginTop: 80 }}>
      <h1>Clinical Conversation AI System</h1>
      <p>Select your role</p>

      <button onClick={() => navigate("/login/patient")}>
        Patient Login
      </button>

      <br /><br />

      <button onClick={() => navigate("/login/doctor")}>
        Doctor Login
      </button>
    </div>
  );
}
