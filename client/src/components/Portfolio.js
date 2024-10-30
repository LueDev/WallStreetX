import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Portfolio = () => {
  const [portfolio, setPortfolio] = useState([]);
  const [totalValue, setTotalValue] = useState(0);

  useEffect(() => {
    const fetchPortfolio = async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5555/api/portfolio', {
        headers: { 'x-access-token': token },
      });

      setPortfolio(response.data);

      // Calculate total portfolio value
      const value = response.data.reduce(
        (acc, stock) => acc + stock.quantity * stock.current_price, 0
      );
      setTotalValue(value);
    };

    fetchPortfolio();
  }, []);

  return (
    <div className="portfolio-container">
      <h1>My Portfolio</h1>
      <h2>Total Value: ${totalValue.toFixed(2)}</h2>

      <table>
        <thead>
          <tr>
            <th>Stock</th>
            <th>Quantity</th>
            <th>Avg Buy Price</th>
            <th>Current Price</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {portfolio.map((stock) => (
            <tr key={stock.stock_symbol}>
              <td>{stock.stock_symbol}</td>
              <td>{stock.quantity}</td>
              <td>${stock.avg_buy_price.toFixed(2)}</td>
              <td>${stock.current_price.toFixed(2)}</td>
              <td>
                <button>Buy</button>
                <button>Sell</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Portfolio;
