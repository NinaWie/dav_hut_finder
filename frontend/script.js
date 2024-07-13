const base_url = 'http://37.120.179.15:4000/get_filtered_huts'

function call_filter_huts() {
    start_lat_input = document.getElementById("latitude").value
    start_lon_input = document.getElementById("longitude").value
    min_distance = document.getElementById("min_distance").value
    max_distance = document.getElementById("max_distance").value
    min_altitude = document.getElementById("min_altitude").value
    max_altitude = document.getElementById("max_altitude").value
    date = document.getElementById("date").value
    const url = base_url + '?start_lat='+ start_lat_input + '&start_lon=' + start_lon_input + "&min_distance=" + min_distance + "&max_distance=" + max_distance + "&min_altitude=" + min_altitude + "&max_altitude=" + max_altitude + "&date=" + date
    fetch(url)
    .then(response => response.text())
    .then(html => {
        console.log(html);
        document.getElementById("demo").innerHTML = html;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
