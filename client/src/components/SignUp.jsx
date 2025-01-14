import React from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useNavigate, Link } from 'react-router-dom';

const host = process.env.REACT_APP_HOST;

const Signup = ({ setToken }) => {
  const navigate = useNavigate();

  const formik = useFormik({
    initialValues: {
      firstName: '',
      lastName: '',
      username: '',
      email: '',
      password: '',
    },
    validationSchema: Yup.object({
      firstName: Yup.string().required('First Name is required'),
      lastName: Yup.string().required('Last Name is required'),
      username: Yup.string().required('Username is required'),
      email: Yup.string().email('Invalid email').required('Email is required'),
      password: Yup.string().min(5, 'Password should be at least 5 characters').required('Password is required'),
    }),
    onSubmit: async (values) => {
      try {
        const response = await fetch(`${host}/user`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(values),
        });

        if (!response.ok) throw new Error('Signup failed');

        const { token } = await response.json();
        localStorage.setItem('token', token);
        setToken(token);
        navigate('/stockpicker');
      } catch (error) {
        console.error('Signup failed:', error);
        alert('Signup failed. Please try again.');
      }
    },
  });

  return (
    <div className="auth-container">
      <div className="auth-banner">
        <h1>Sign Up</h1>
      </div>
      <form onSubmit={formik.handleSubmit} className="auth-form">
        <input
          type="text"
          name="firstName"
          placeholder="First Name"
          value={formik.values.firstName}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          className="input-field"
        />
        {formik.touched.firstName && formik.errors.firstName ? <div>{formik.errors.firstName}</div> : null}

        <input
          type="text"
          name="lastName"
          placeholder="Last Name"
          value={formik.values.lastName}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          className="input-field"
        />
        {formik.touched.lastName && formik.errors.lastName ? <div>{formik.errors.lastName}</div> : null}

        <input
          type="text"
          name="username"
          placeholder="Username"
          value={formik.values.username}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          className="input-field"
        />
        {formik.touched.username && formik.errors.username ? <div>{formik.errors.username}</div> : null}

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formik.values.email}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          className="input-field"
        />
        {formik.touched.email && formik.errors.email ? <div>{formik.errors.email}</div> : null}

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formik.values.password}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          className="input-field"
        />
        {formik.touched.password && formik.errors.password ? <div>{formik.errors.password}</div> : null}

        <button type="submit" className="button">Sign Up</button>
      </form>
      <div className="auth-link">
        Already have an account? <Link to="/login">Login →</Link>
      </div>
    </div>
  );
};

export default Signup;
