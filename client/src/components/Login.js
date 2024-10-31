import React from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

host = process.env.REACT_APP_HOST

const Login = ({ setToken }) => {
  const navigate = useNavigate();

  // Yup validation schema
  const validationSchema = Yup.object({
    username: Yup.string().required('Username is required'),
    password: Yup.string()
      .min(5, 'Password must be at least 5 characters')
      .required('Password is required'),
  });

  const handleLogin = async (values, { setSubmitting }) => {
    try {
      const response = await axios.post(host+'/login', values);
      const { token } = response.data;

      localStorage.setItem('token', token);
      setToken(token);
      navigate('/stockpicker');
    } catch (error) {
      console.error('Invalid login:', error);
      alert('Login failed. Please check your credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-banner">
        <h1>Wall Street X</h1>
        <p>Your gateway to trading smart</p>
      </div>
      <Formik
        initialValues={{ username: '', password: '' }}
        validationSchema={validationSchema}
        onSubmit={handleLogin}
      >
        {({ isSubmitting }) => (
          <Form className="login-form">
            <div>
              <Field
                type="text"
                name="username"
                placeholder="Username"
                className="input-field"
              />
              <ErrorMessage
                name="username"
                component="div"
                className="error-message"
              />
            </div>

            <div>
              <Field
                type="password"
                name="password"
                placeholder="Password"
                className="input-field"
              />
              <ErrorMessage
                name="password"
                component="div"
                className="error-message"
              />
            </div>

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Logging in...' : 'Login'}
            </button>
          </Form>
        )}
      </Formik>
      <div className="signup-link">
        <p>No account? <Link to="/signup">Sign up here &rarr;</Link></p>
      </div>
    </div>
  );
};

export default Login;
