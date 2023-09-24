import { createBrowserRouter, RouterProvider } from "react-router-dom";

import "./App.css";
import Home from "./components/pages/Home";
import Root from "./components/pages/Root";
import Services from "./components/pages/Services";
import Product from "./components/pages/Product";
import SignUp from "./components/pages/SignUp";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/services", element: <Services /> },
      { path: "/products", element: <Product /> },
      { path: "/sign-up", element: <SignUp /> },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
