import Typical from "react-typical";

export default function MovingText() {
  return (
    <h2 className="typical-text">
      <Typical
        steps={[
          "Track patients", 2000,
          "View history", 2000,
          "Record audio", 2000
        ]}
        loop={Infinity}
        wrapper="span"
      />
    </h2>
  );
}

import { Tabs, Tab, Box } from "@mui/material";
import { motion } from "framer-motion";

export default function AnimatedTabs({ value, setValue }) {
  return (
    <Tabs
      value={value}
      onChange={(e,v) => setValue(v)}
      centered
      textColor="secondary"
      indicatorColor="secondary"
    >
      {["Dashboard", "History", "Recorder", "Analytics"].map((label, i) => (
        <Tab
          key={i}
          label={
            <motion.div
              whileHover={{ scale: 1.2 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              {label}
            </motion.div>
          }
        />
      ))}
    </Tabs>
  );
}
