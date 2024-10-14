// Define the function separately
function handleCsvData(err, rows) {
  if (err) {
    console.error('Error loading CSV data:', err);
    return;
  }

  // Get unique reasons from the CSV data
  const uniqueReasons = [...new Set(rows.map(row => row['Reason']))].sort();

  // Create a trace for each reason
  const data = uniqueReasons.map(reason => {
    return {
      type: "scattermapbox",
      lon: rows
        .filter(row => row['Reason'] === reason)
        .map(row => row['long']),
      lat: rows
        .filter(row => row['Reason'] === reason)
        .map(row => row['lat']),
      text: rows
        .filter(row => row['Reason'] === reason)
        .map(row => row['Reason']),
      customdata: rows
        .filter(row => row['Reason'] === reason)
        .map(row => row['Date'] + "<br>" + row['Reason'] + "<br>" + row['Address'] + "<br>" + row['Normalized_Address']),
      hovertemplate: '%{customdata}',
      name: reason, // This sets the legend label
      marker: {
        size: 8,
        opacity: 0.8
      }
    };
  });

  var config = { responsive: true };

  var layout = {
    autosize: true,
    mapbox: {
      center: { lat: 42.284955, lon: -71.347789 },
      style: "open-street-map",
      zoom: 12
    },
    margin: { r: 0, t: 0, b: 0, l: 0 },
    hoverlabel: { align: "left" },
    showlegend: true,  // Enable legend display
    legend: {
      orientation: "h", // Horizontal legend (you can change to 'v' for vertical)
      x: 0.5,
      xanchor: "center",
      y: -0.1,
      yanchor: "top"
    }
  };

  Plotly.newPlot("myDiv", data, layout, config);
}

// Call the d3.csv with the separate function
d3.csv(
  "https://raw.githubusercontent.com/nikconwell/location/main/activity.csv",
  handleCsvData
);
