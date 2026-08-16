import { createContext, useContext, useEffect, useState } from "react";
import { api } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(undefined); // undefined = loading

  useEffect(() => {
    const token = localStorage.getItem("meta_token");
    if (!token) {
      setUser(null);
      return;
    }
    api
      .get("/auth/me")
      .then((r) => setUser(r.data))
      .catch(() => {
        localStorage.removeItem("meta_token");
        setUser(null);
      });
  }, []);

  async function login(email, password) {
    const { data } = await api.post("/auth/login", { email, password });
    localStorage.setItem("meta_token", data.token);
    setUser(data.user);
    return data.user;
  }

  async function logout() {
    try {
      await api.post("/auth/logout");
    } catch (e) {
      /* ignore */
    }
    localStorage.removeItem("meta_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
