import React, { useEffect, useState } from 'react';
import axios from 'axios';

const host = process.env.REACT_APP_HOST;

const TradeHistory = () => {
  const [trades, setTrades] = useState([]);
  const token = localStorage.getItem('token'); // Token from localStorage

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        const response = await axios.get(`${host}/api/trade-history`, {
          headers: { 'x-access-token': token },
        });
        setTrades(response.data);
      } catch (error) {
        console.error('Error fetching trade history:', error);
      }
    };

    fetchTrades();
  }, [token]);

  return (
    <div className="trade-history">
      <h2>Trade History</h2>
      <table>
        <thead>
          <tr>
            <th>Stock Symbol</th>
            <th>Trade Type</th>
            <th>Quantity</th>
            <th>Price at Trade</th>
            <th>Net Profit</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade, index) => (
            <tr key={index}>
              <td>{trade.stock_symbol || 'N/A'}</td>
              <td>{trade.trade_type || 'N/A'}</td>
              <td>{trade.quantity || 0}</td>
              <td>
                {trade.price_at_trade !== null && trade.price_at_trade !== undefined
                  ? `$${trade.price_at_trade.toFixed(2)}`
                  : 'N/A'}
              </td>
              <td>
                {trade.net_profit !== null && trade.net_profit !== undefined
                  ? `$${trade.net_profit.toFixed(2)}`
                  : 'N/A'}
              </td>
              <td>{new Date(trade.timestamp).toLocaleString() || 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TradeHistory;
