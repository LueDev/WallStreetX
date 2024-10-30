import React, { useEffect, useState } from 'react';
import axios from 'axios';

const TradeHistory = () => {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    const fetchTradeHistory = async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5555/api/trade-history', {
        headers: { 'x-access-token': token },
      });

      setTrades(response.data);
    };

    fetchTradeHistory();
  }, []);

  return (
    <div className="trade-history-container">
      <h1>Trade History</h1>
      <table>
        <thead>
          <tr>
            <th>Stock</th>
            <th>Type</th>
            <th>Quantity</th>
            <th>Price at Trade</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={trade.timestamp}>
              <td>{trade.stock_symbol}</td>
              <td>{trade.trade_type}</td>
              <td>{trade.quantity}</td>
              <td>${trade.price_at_trade.toFixed(2)}</td>
              <td>{new Date(trade.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TradeHistory;
