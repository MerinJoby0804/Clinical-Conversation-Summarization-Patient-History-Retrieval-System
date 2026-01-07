import api from "./api";

export const loginUser = async (email, password, role) => {
  const res = await api.post("/login", {
    email,
    password,
    role,
  });

  localStorage.setItem("token", res.data.token);
  localStorage.setItem("role", res.data.role);

  return res.data;
};
