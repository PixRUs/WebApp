
    document.addEventListener("DOMContentLoaded", function() {
        const chartData = JSON.parse(document.getElementById('chart-data').textContent);
        console.log(chartData)
    window.ApexCharts && (new ApexCharts(document.getElementById('performance-chart'), {
    chart: {
    type: "line",
    fontFamily: 'inherit',
    height: 240,
    parentHeightOffset: 0,
    toolbar: {
    show: false,
},
    animations: {
    enabled: false
},
},
    series: chartData.series,
    xaxis: {
    categories: chartData.labels,
    labels: {
    padding: 0,
},
},
    stroke: {
    width: 2,
    lineCap: "round",
    curve: "straight",
},
    legend: {
    show: true,
    position: 'bottom',
},
})).render();
});
