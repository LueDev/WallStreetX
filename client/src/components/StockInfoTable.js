import React from 'react';

const StockInfoTable = ({ stock }) => {
  if (!stock || Object.keys(stock).length === 0) {
    return <p>No stock selected. Please select a stock to view its details.</p>;
  }

  return (
    <div className="stock-info">
      <h2>Stock Information</h2>
      <table className="stock-info-table">
        <tbody>
          <tr>
            <td><strong>Current Price:</strong></td>
            <td>${stock.currentPrice}</td>
          </tr>
          <tr>
            <td><strong>Daily Change:</strong></td>
            <td>{stock.dailyChange}</td>
          </tr>
          <tr>
            <td><strong>Percent Change:</strong></td>
            <td>{stock.percentChange}</td>
          </tr>
          <tr>
            <td><strong>Technical Rating:</strong></td>
            <td>{stock.technicalRating}</td>
          </tr>
          <tr>
            <td><strong>Market Cap:</strong></td>
            <td>${stock.marketCap}</td>
          </tr>
          <tr>
            <td><strong>Volume:</strong></td>
            <td>{stock.volume}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default StockInfoTable;
