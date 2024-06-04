function demo_javascript_method() {
    start_lat_input = document.getElementById("latitude").value
    start_lon_input = document.getElementById("longitude").value
    const url = 'http://localhost:8989/compute_route?start_lat=' + start_lat_input + '&start_lon=' + start_lon_input
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            document.getElementById("demo").innerHTML = JSON.stringify(json)
        })
}