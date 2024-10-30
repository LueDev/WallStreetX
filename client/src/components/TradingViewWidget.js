import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

const TradingViewWidget = ({ data }) => {
  const chartContainerRef = useRef();

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 420,
      layout: {
        backgroundColor: '#ffffff',
        textColor: '#000000',
      },
      timeScale: {
        timeVisible: true,
        borderColor: '#cccccc',
        tickMarkFormatter: (time) => new Date(time * 1000).toLocaleDateString(),
      },
      grid: {
        vertLines: { color: '#e0e0e0' },
        horzLines: { color: '#e0e0e0' },
      },
    });

    const candlestickSeries = chart.addCandlestickSeries();
    candlestickSeries.setData(data); // Now using correctly formatted data

    return () => chart.remove(); // Cleanup on unmount
  }, [data]);

  return <div ref={chartContainerRef} className="chart-container" />;
};

export default TradingViewWidget;
