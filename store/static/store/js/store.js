/* store.js
luke hutton 2017 */

// radar plot
// show summary results

function buildChart(ranks) {
  var ctx = document.getElementById("profileResult");
  var myChart = new Chart(ctx, {
      type: 'radar',
      data: {
          labels: ["Notice", "Consent", "Access", "Social"],
          datasets: [{
              label: 'How important this is to you',
              data: [ranks.notice, ranks.consent, ranks.access,ranks.social],
              backgroundColor: "rgba(179,181,198,0.2)",
              borderColor: "rgba(179,181,198,1)",
              pointBackgroundColor: "rgba(179,181,198,1)",
              pointBorderColor: "#fff",
              pointHoverBackgroundColor: "#fff",
              pointHoverBorderColor: "rgba(179,181,198,1)"
          }
        ]

      },
      options: {
        scale: {
                reverse: false,
                ticks: {
                    display: false,
                    stepSize: 10,
                },
                gridLines: {
                  color: "rgba(0,0,0,0.1)"
                },
                yAxes: [{
                gridLines: {
                  displayOnChartArea: false, // hides the grid lines from this axis
                }
              }]
            }
      }
  });
}
