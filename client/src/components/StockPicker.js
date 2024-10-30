import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import TradingViewWidget from './TradingViewWidget';
import StockInfoTable from './StockInfoTable';

const StockPicker = () => {
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [quantity, setQuantity] = useState('');
  const [tradeType, setTradeType] = useState('buy');
  const [feedback, setFeedback] = useState('');
  const [stockInfo, setStockInfo] = useState({});
  const [token, setToken] = useState(localStorage.getItem('token')); // Token state
  const intervalRef = useRef(null);

  // Fetch stocks from the backend when token is available
  const fetchStocks = async () => {
    if (!token) {
      alert('No token found. Please log in.');
      return;
    }

    try {
      const response = await axios.get('http://localhost:5555/api/stocks', {
        headers: { 'x-access-token': token },
      });

      const fetchedStocks = response.data;
      setStocks(fetchedStocks);

      if (fetchedStocks.length > 0) {
        setSelectedStock(fetchedStocks[0]);
        fetchHistoricalData(fetchedStocks[0].symbol); // Fetch historical data
      }
    } catch (error) {
      console.error('Error fetching stocks:', error);
      alert('Failed to fetch stocks. Please log in again.');
    }
  };

  // Fetch historical data for a stock from the backend
  const fetchHistoricalData = async (symbol) => {
    try {
      const response = await axios.get(
        `http://localhost:5555/api/historical/${symbol}`,
        { headers: { 'x-access-token': token } }
      );
  
      let data = response.data.prices; // Assuming 'prices' contains the historical data
  
      // Ensure data is sorted by 'date' in ascending order
      const sortedData = data.sort((a, b) => a.date - b.date);
  
      // Remove duplicate timestamps
      const uniqueData = sortedData.filter((item, index, array) => {
        return index === 0 || item.date !== array[index - 1].date;
      });
  
      // Map to the format required by the chart
      const formattedData = uniqueData.map((item) => ({
        time: item.date, // Ensure this is in seconds, not milliseconds
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }));
  
      setHistoricalData(formattedData); // Store the cleaned data in state
      updateStockInfo(formattedData); // Update stock info
    } catch (error) {
      console.error('Error fetching historical data:', error);
    }
  };
  
  

  // Update stock information based on historical data
  const updateStockInfo = (data) => {
    if (data.length > 0) {
      const latest = data[data.length - 1];
      const previous = data[data.length - 2] || latest;

      const dailyChange = (latest.close - previous.close).toFixed(2);
      const percentChange = ((dailyChange / previous.close) * 100).toFixed(2);
      const technicalRating = dailyChange >= 0 ? 'Buy' : 'Sell';

      setStockInfo({
        currentPrice: latest.close.toFixed(2),
        dailyChange,
        percentChange: `${percentChange}%`,
        technicalRating,
      });
    }
  };

  // Handle trade submission
  const handleTradeSubmit = async (event) => {
    event.preventDefault();

    if (!selectedStock) {
      alert('Please select a stock before executing a trade.');
      return;
    }

    const tradeData = {
      stock_id: selectedStock.id,
      trade_type: tradeType,
      quantity: parseInt(quantity),
      price_at_trade: selectedStock.current_price,
      timestamp: new Date().toISOString(),
    };

    try {
      const response = await axios.post(
        'http://localhost:5555/api/trades',
        tradeData,
        { headers: { 'x-access-token': token } }
      );

      setFeedback(response.data.message);
      setQuantity('');
    } catch (error) {
      console.error('Trade execution failed:', error);
      setFeedback('Trade failed. Please try again.');
    }
  };

  // Fetch stocks on component mount if token is available
  useEffect(() => {
    if (token) fetchStocks();
  }, [token]);

  // Fetch historical data when the selected stock changes
  useEffect(() => {
    if (selectedStock) {
      fetchHistoricalData(selectedStock.symbol);
    }
  }, [selectedStock]);

  return (
    <div className="container">
      <h1>Stock Picker</h1>

      <select
        value={selectedStock?.id || ''}
        onChange={(e) =>
          setSelectedStock(
            stocks.find((stock) => stock.id === parseInt(e.target.value))
          )
        }
      >
        {stocks.map((stock) => (
          <option key={stock.id} value={stock.id}>
            {stock.company_name} ({stock.symbol})
          </option>
        ))}
      </select>

      <div className="chart-and-sidebar">
        <div className="chart-container">
          {selectedStock && historicalData.length > 0 ? (
            <TradingViewWidget symbol={selectedStock.symbol} data={historicalData} />
          ) : (
            <p>Loading chart data...</p>
          )}
        </div>

        <div className="sidebar">
          <form onSubmit={handleTradeSubmit} className="trade-form">
            <h2>Execute Trade</h2>
            <input
              type="number"
              placeholder="Quantity"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
            />
            <select
              value={tradeType}
              onChange={(e) => setTradeType(e.target.value)}
            >
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
            <button type="submit">Submit Trade</button>
          </form>
          {feedback && <p>{feedback}</p>}
        </div>
      </div>

      <StockInfoTable stock={stockInfo} />
    </div>
  );
};

export default StockPicker;
