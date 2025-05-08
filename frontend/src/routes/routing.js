import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Home from "../components/Home";
import ListProduct from "../components/ListProduct";
import Why from "../components/Why";
import Testimonial from "../components/Testimonial";
import Contact from "../components/Contact";
import Login from "../components/Login";
import Register from "../components/Register";
import Cart from "../components/Cart";
import NotFound404 from '../components/NotFound404';
import AuthenRoute from "../features/auth/AuthRoute";
import ChatPage from "../components/Chat";
import PaymentHistory from "../components/PaymentHistory";
import ProductDetailPage from "../components/ProductDetail";
import CrawlTool from "../components/Crawl";
import StoreCrawl from "../components/StoreCrawl";
import FaceID from '../components/FaceID';

function RouteProject() {

  const router = createBrowserRouter([
    {
      path: '/',
      element: <Home />,
      errorElement: <NotFound404 />
    },
    {
      path: '/shop',
      element: <ListProduct />,
    },
    {
      path: '/why',
      element: <Why />,
    },
    {
      path: '/testimonial',
      element: <Testimonial />,
    },
    {
      path: '/contact',
      element: <Contact />,
    },
    {
      path: '/login',
      element: <Login />,
    },
    {
      path: '/register',
      element: <Register />,
    },
    {
      path: '/productdetail/:id',
      element: <ProductDetailPage />,
    },
    {
      path: '/cart',
      element: (
        <AuthenRoute>
          <Cart />
        </AuthenRoute>
      ),
    },
    {
      path: '/payment-history',
      element:
        <AuthenRoute>
          <PaymentHistory />
        </AuthenRoute>
      ,
    },
    {
      path: '/loginFaceId',
      element:
        <FaceID />
    },
    {
      path: '/Chat',
      element: <ChatPage />,
    },
    {
      path: '/Crawl',
      element: <CrawlTool />
    },
    {
      path: '/storecrawl',
      element: <StoreCrawl />
    }
  ])

  return (
    <div>
      <RouterProvider router={router} />
    </div>
  )
}

export default RouteProject;