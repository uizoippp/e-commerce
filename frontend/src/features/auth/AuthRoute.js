import React from "react";
import { Navigate } from "react-router-dom";

// Kiểm tra token trong localStorage
const AuthenRoute = ({ children }) => {
  const token = localStorage.getItem("token");

  if (!token) {
    // Chưa đăng nhập → chuyển hướng về trang login
    return <Navigate to="/login" />;
  }

  // Đã đăng nhập → cho phép render component con
  return children;
};

export default AuthenRoute;
