import React, { useState } from "react";
import {
  Paper,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from "@mui/material";

function PatientHistory({ patients, deletePatient, clearPatients }) {
  const [openClearDialog, setOpenClearDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(null);

  const handleDeleteClick = (index) => {
    setSelectedIndex(index);
    setOpenDeleteDialog(true);
  };

  const confirmDelete = () => {
    deletePatient(selectedIndex);
    setOpenDeleteDialog(false);
    setSelectedIndex(null);
  };

  const confirmClear = () => {
    clearPatients();
    setOpenClearDialog(false);
  };

  return (
    <Paper elevation={3} sx={{ p: 4, m: 3 }}>
      <Typography variant="h4" gutterBottom color="secondary">
        Patient History
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Age</TableCell>
            <TableCell>Gender</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {patients.map((p, index) => (
            <TableRow key={index}>
              <TableCell>{p.name}</TableCell>
              <TableCell>{p.age}</TableCell>
              <TableCell>{p.gender}</TableCell>
              <TableCell>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={() => handleDeleteClick(index)}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {patients.length > 0 && (
        <Button
          variant="contained"
          color="error"
          onClick={() => setOpenClearDialog(true)}
          style={{ marginTop: "20px" }}
        >
          Clear All Patients
        </Button>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={openDeleteDialog} onClose={() => setOpenDeleteDialog(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          Are you sure you want to delete this patient?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
          <Button color="error" onClick={confirmDelete}>Delete</Button>
        </DialogActions>
      </Dialog>

      {/* Clear All Confirmation Dialog */}
      <Dialog open={openClearDialog} onClose={() => setOpenClearDialog(false)}>
        <DialogTitle>Confirm Clear All</DialogTitle>
        <DialogContent>
          Are you sure you want to clear all patients?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenClearDialog(false)}>Cancel</Button>
          <Button color="error" onClick={confirmClear}>Clear All</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}

export default PatientHistory;


