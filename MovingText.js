import React, { useEffect, useState } from "react";

const texts = [
  "Track Patients 🧑‍⚕️",
  "View History 📄",
  "Record Consultations 🎙️",
  "Analyze Data 📊",
];

function MovingText() {
  const [textIndex, setTextIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [displayText, setDisplayText] = useState("");

  useEffect(() => {
    if (charIndex < texts[textIndex].length) {
      const timeout = setTimeout(() => {
        setDisplayText((prev) => prev + texts[textIndex][charIndex]);
        setCharIndex(charIndex + 1);
      }, 80);

      return () => clearTimeout(timeout);
    } else {
      const pause = setTimeout(() => {
        setDisplayText("");
        setCharIndex(0);
        setTextIndex((textIndex + 1) % texts.length);
      }, 1500);

      return () => clearTimeout(pause);
    }
  }, [charIndex, textIndex]);

  return (
    <h2
      style={{
        marginTop: "12px",
        fontSize: "1.5rem",
        fontWeight: 500,
        minHeight: "2rem",
      }}
    >
      {displayText}
    </h2>
  );
}

export default MovingText;
