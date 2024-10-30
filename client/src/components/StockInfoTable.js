// client/src/components/StockInfoTable.js
import React from 'react';

const StockInfoTable = ({ stockData }) => {
  const {
    currentPrice = 'N/A',
    dailyChange = 'N/A',
    percentChange = 'N/A',
    technicalRating = 'N/A',
  } = stockData || {};

  return (
    <div className="stock-info-container">
      <h3>{`Overview`}</h3>
      <table className="stock-info-table">
        <thead>
          <tr>
            <th>Current Price</th>
            <th>Daily Change</th>
            <th>Percent Change</th>
            <th>Technical Rating</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>${currentPrice}</td>
            <td>{dailyChange}</td>
            <td>{percentChange}%</td>
            <td>{technicalRating}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default StockInfoTable;
