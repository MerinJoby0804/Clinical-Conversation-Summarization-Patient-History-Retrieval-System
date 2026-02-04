import React from "react";
import { motion } from "framer-motion";
import { User, Stethoscope } from "lucide-react";
import "./RoleSelect.css";

function RoleSelect({ onSelect }) {
  return (
    <div className="role-bg">
      <motion.h1
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        className="role-title"
      >
        Clinical AI System
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="role-subtitle"
      >
        Who are you?
      </motion.p>

      <div className="role-cards">
        {/* Doctor */}
        <motion.div
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.95 }}
          className="role-card doctor"
          onClick={() => onSelect("doctor")}
        >
          <Stethoscope size={60} />
          <h2>Doctor</h2>
          <p>Record • Analyze • Summarize</p>
        </motion.div>

        {/* Patient */}
        <motion.div
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.95 }}
          className="role-card patient"
          onClick={() => onSelect("patient")}
        >
          <User size={60} />
          <h2>Patient</h2>
          <p>View History • Understand Care</p>
        </motion.div>
      </div>
    </div>
  );
}

export default RoleSelect;
