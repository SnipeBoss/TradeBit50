/*
 Create chart by using candlestick data
 src documentation : 
 - https://github.com/tradingview/lightweight-charts
 - https://jsfiddle.net/TradingView/eaod9Lq8/
*/

// Chart Configuration to div charts src : https://jsfiddle.net/TradingView/eaod9Lq8/
var chart = LightweightCharts.createChart(document.getElementById("candlestick_chart"), 
{
  width: 1360, // default 600
  height: 675, // default 300
  layout: {
    background: {
      type: 'solid',
      color: '#ffffff', // Change to white
    },
    textColor: 'rgba(0, 0, 0, 0.9)', // Change to black with 90% opacity
  },
  grid: {
    vertLines: {
      color: 'rgba(0, 0, 0, 0.5)', // Change to black with 50% opacity
    },
    horzLines: {
      color: 'rgba(0, 0, 0, 0.5)', // Change to black with 50% opacity
    },
  },
  crosshair: {
    mode: LightweightCharts.CrosshairMode.Normal,
  },
  rightPriceScale: {
    borderColor: 'rgba(0, 0, 0, 0.8)', // Change to black with 80% opacity
  },
  timeScale: {
    borderColor: 'rgba(0, 0, 0, 0.8)', // Change to black with 80% opacity
  },
});


// Style and Chart Candle stick src : https://jsfiddle.net/TradingView/eaod9Lq8/
var candleSeries = chart.addCandlestickSeries({
  upColor: '#00ff00',
  downColor: '#ff0000',
  borderDownColor: '#ff0000',
  borderUpColor: '#00ff00',
  wickDownColor: '#ff0000',
  wickUpColor: '#00ff00',
});

// Data Fetching src : https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#sending_a_request_with_credentials_included
fetch("http://127.0.0.1:5000/history")
  .then((response) => response.json())
  .then((response) => {
    console.log("Candlestick Data:", response);
    candleSeries.setData(response);
  })

// Connected to Binance Websocket stream
// Websocket src : https://github.com/binance-us/binance-us-api-docs/blob/master/web-socket-streams.md
var binanceSocket = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@kline_5m");

binanceSocket.onmessage = function(event){
	// Parse JSON String coming in
	var message = JSON.parse(event.data);

	// k is the key of the object
	var candlestick = message.k;
	console.log(candlestick)

	// Update Candlestick realtime src: https://tradingview.github.io/lightweight-charts/docs
	candleSeries.update({
		time: candlestick.t / 1000,
		open : candlestick.o,
		high : candlestick.h,
		low : candlestick.l,
		close : candlestick.c
	});
};