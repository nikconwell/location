d3.csv(
  "https://raw.githubusercontent.com/nikconwell/location/main/activity.csv",
  function (err, rows) {
    function unpack(rows, key) {
      return rows.map((row) => row[key]);
    }
//      return rows.map(function (row) {
//        return row[key];
//      });
    var data = [
      {
        type: "scattermapbox",
        lon: unpack(rows, "long"),
        lat: unpack(rows, "lat"),
        text: unpack(rows, "normalized"),
        hovertext: unpack(rows, "Reason"),
        zoom: 8,
        marker: {
          size: 8,
          opacity: 0.8,
          color: "black"
        }
      }
    ];

    var layout = {
      mapbox: {
        center: { lat: 42.284955, lon: -71.347789 },
        style: "open-street-map",
        zoom: 12
      },
      dragmode: "zoom",
      margin: { r: 0, t: 0, b: 0, l: 0 }
    };

    Plotly.newPlot("myDiv", data, layout);
  }
);
