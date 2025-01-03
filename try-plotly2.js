// Define the function separately
function handleCsvData(err, rows) {
  if (err) {
    console.error('Error loading CSV data:', err);
    return;
  }

  // Get unique reasons from the CSV data
  const uniqueReasons = [...new Set(rows.map(row => row['Normalized_Reason']))].sort();

  // Create a trace for each reason
  const data = uniqueReasons.map(reason => {
    return {
      type: "scattermapbox",
      lon: rows
        .filter(row => row['Normalized_Reason'] === reason)
        .map(row => row['long']),
      lat: rows
        .filter(row => row['Normalized_Reason'] === reason)
        .map(row => row['lat']),
      text: rows
        .filter(row => row['Normalized_Reason'] === reason)
        .map(row => row['Normalized_Reason']),
      customdata: rows
        .filter(row => row['Normalized_Reason'] === reason)
        .map(row => row['Date'] + "<br>" + row['Log_Reason'] + "<br>" + row['Log_Address'] + "<br>" + row['Normalized_Address']),
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
    title: {text: 'Town of Natick Activity'},
    autosize: true,
    mapbox: {
      center: { lat: 42.284955, lon: -71.347789 },
      style: "open-street-map",
      zoom: 13
    },
    margin: { r: 20, t: 40, b: 20, l: 20, pad: 0 },
    hoverlabel: { align: "left" },
    showlegend: true,  // Enable legend display
    // legend: {
    //   orientation: "h", // Horizontal legend (you can change to 'v' for vertical)
    //   x: 0.5,
    //   xanchor: "center",
    //   y: -0.1,
    //   yanchor: "top"
    // }
  };

  Plotly.newPlot("myDiv", data, layout, config);
}

// Call the d3.csv with the separate function
d3.csv(
  "https://raw.githubusercontent.com/nikconwell/location/main/activity.csv",
  handleCsvData
);
