import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Portfolio = () => {
  const [portfolio, setPortfolio] = useState([]);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:5555/api/portfolio', {
          headers: { 'x-access-token': token },
        });
        setPortfolio(response.data);
      } catch (error) {
        console.error('Error fetching portfolio data:', error);
      }
    };

    fetchPortfolio();
  }, []);

  return (
    <div className="portfolio">
      <h2>Portfolio Summary</h2>
      <table>
        <thead>
          <tr>
            <th>Stock</th>
            <th>Quantity</th>
            <th>Avg Buy Price</th>
            <th>Current Price</th>
            <th>Current Value</th>
            <th>Net Profit/Loss</th>
          </tr>
        </thead>
        <tbody>
          {portfolio.map((entry) => (
            <tr key={entry.stock_symbol}>
              <td>{entry.stock_symbol}</td>
              <td>{entry.quantity}</td>
              <td>${entry.avg_buy_price ? entry.avg_buy_price.toFixed(2) : 'N/A'}</td>
              <td>${entry.current_price ? entry.current_price.toFixed(2) : 'N/A'}</td>
              <td>${entry.current_value ? entry.current_value.toFixed(2) : 'N/A'}</td>
              <td>${entry.net_profit_loss ? entry.net_profit_loss.toFixed(2) : 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Portfolio;
