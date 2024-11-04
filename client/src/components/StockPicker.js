import React, { useState, useEffect, useRef } from 'react';
import TradingViewWidget from './TradingViewWidget';
import StockInfoTable from './StockInfoTable';

const host = process.env.REACT_APP_HOST;

const StockPicker = () => {
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [quantity, setQuantity] = useState('');
  const [tradeType, setTradeType] = useState('buy');
  const [feedback, setFeedback] = useState('');
  const [stockInfo, setStockInfo] = useState({});
  const [token, setToken] = useState(localStorage.getItem('token'));
  const intervalRef = useRef(null);

  // Fetch stocks from the backend when token is available
  const fetchStocks = async () => {
    if (!token) {
      alert('No token found. Please log in.');
      return;
    }

    try {
      const response = await fetch(`${host}/api/stocks`, {
        headers: { 'x-access-token': token },
      });

      if (!response.ok) throw new Error('Failed to fetch stocks');

      const fetchedStocks = await response.json();
      setStocks(fetchedStocks);

      if (fetchedStocks.length > 0) {
        setSelectedStock(fetchedStocks[0]);
        fetchHistoricalData(fetchedStocks[0].symbol);
      }
    } catch (error) {
      console.error('Error fetching stocks:', error);
      alert('Failed to fetch stocks. Please log in again.');
    }
  };

  // Fetch historical data for a stock from the backend
  const fetchHistoricalData = async (symbol) => {
    try {
      const response = await fetch(`${host}/api/historical/${symbol}`, {
        headers: { 'x-access-token': token },
      });

      if (!response.ok) throw new Error('Failed to fetch historical data');

      const data = await response.json();
      const sortedData = data.sort((a, b) => new Date(a.date) - new Date(b.date));
      const uniqueData = sortedData.filter((item, index, array) => index === 0 || item.date !== array[index - 1].date);

      const formattedData = uniqueData.map((item) => ({
        time: item.date,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }));

      setHistoricalData(formattedData);
      updateStockInfo(formattedData);

      // Update current price in the database
      const latestPrice = formattedData[formattedData.length - 1]?.close;
      if (latestPrice) {
        await fetch(`${host}/api/update_stock_price`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-access-token': token,
          },
          body: JSON.stringify({ symbol, latest_price: latestPrice }),
        });
      }
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
    };

    try {
      const response = await fetch(`${host}/api/trades`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-access-token': token,
        },
        body: JSON.stringify(tradeData),
      });

      if (!response.ok) throw new Error('Trade execution failed');

      const data = await response.json();
      setFeedback(data.message);
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
