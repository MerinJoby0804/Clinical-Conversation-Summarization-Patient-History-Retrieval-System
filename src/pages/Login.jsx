import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import { loginUser } from "../services/auth";

export default function Login() {
  const { role } = useParams();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const data = await loginUser(email, password, role);
      navigate(`/${data.role}`);
    } catch {
      alert("Login failed");
    }
  };

  return (
    <div>
      <h2>{role.toUpperCase()} LOGIN</h2>

      <input
        placeholder="Email"
        onChange={(e) => setEmail(e.target.value)}
      /><br />

      <input
        type="password"
        placeholder="Password"
        onChange={(e) => setPassword(e.target.value)}
      /><br />

      <button onClick={handleLogin}>Login</button>
    </div>
  );
}
