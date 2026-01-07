import RecordSymptoms from "./RecordSymptoms";
import PatientHistory from "./PatientHistory";

export default function PatientDashboard() {
  return (
    <div>
      <h2>Patient Dashboard</h2>
      <RecordSymptoms />
      <PatientHistory />
    </div>
  );
}
