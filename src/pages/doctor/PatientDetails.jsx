import { useParams } from "react-router-dom";

export default function PatientDetails() {
  const { id } = useParams();

  return (
    <div>
      <h3>Patient Details</h3>
      <p>Patient ID: {id}</p>

      <ul>
        <li>10/08/2025 – Viral Fever</li>
        <li>22/09/2025 – Chest Pain</li>
      </ul>
    </div>
  );
}
