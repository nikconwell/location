function handleCSVData(err,rows) {

  var data = [
    {
      type: "scattermapbox",
      lon: rows.map((row) => row['long']),
      lat: rows.map((row) => row['lat']),
      text: rows.map((row) => row['Reason']),
      customdata: rows.map((row => row['Date'] + "<br>" + 
                            row['Reason'] + "<br>" + 
                            row['Address'] + "<br>" + 
                            row['Normalized_Address'])),
      hovertemplate: '%{customdata}',
      name: "",
      zoom: 8,
      marker: {
        size: 8,
        opacity: 0.8,
        color: "black"
      }
    }
  ];

  var config={responsive: true};

  var layout = {
    autosize: true,
    mapbox: {
      center: { lat: 42.284955, lon: -71.347789 },
      style: "open-street-map",
      zoom: 12
    },
    margin: { r: 0, t: 0, b: 0, l: 0 },
    hoverlabel: { align: "left"},
  };

  Plotly.newPlot("myDiv", data, layout, config);
}




d3.csv(
  "https://raw.githubusercontent.com/nikconwell/location/main/activity.csv",
  handleCSVData
);
