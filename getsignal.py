'''
getsignal.py grabs the rssi and sinr from the router every 30 seconds and saves the output to rssi.json and sinr.json
this is the first component of an SDK app to re-add the rssi and sinr graphs to our routers ui
'''

try:
    import cs
    import sys
    import traceback
    import os.path
    import json
    import time

    from app_logging import AppLogger

except Exception as ex:
    # Output DEBUG logs indicating what import failed. Use the logging in the
    # CSClient since app_logging may not be loaded.
    cs.CSClient().log('getsignal.py', 'Import failure: {}'.format(ex))
    cs.CSClient().log('getsignal.py', 'Traceback: {}'.format(traceback.format_exc()))
    sys.exit(-1)

# Create an AppLogger for logging to syslog in NCOS.
log = AppLogger()
log.debug('Started getsignal.py')

# initialize rssi and sinr lists
rssi = []
sinr = []

# js block
js_block = """
var values = %s;
var ctx = document.getElementById("%sChart").getContext('2d');
var scatterChart = new Chart(ctx, {
    type: 'scatter',
    data: {
        datasets: [{
            label: '%s',
            backgroundColor: 'rgb(173, 117, 117)',
            borderColor: 'rgb(216, 114, 114)',
            showLine:true,
            fill:false,
            lineTension:0,
            data: values,
        }]
    },
    options: {
        responsive: true,
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Time'
                }
            }],
            yAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
            }]
        }
    }
});
"""


# this function is used to initialize the RSSI and SINR on first run of the program
def initializevalues():
    log.debug('Initializing Graph values')
    try:
        # get the time
        router_time = cs.CSClient().get('/status/system/time/')
        router_time = int(router_time['data'])
        for i in range(50):
            # every loop, subtract 30 seconds from the time to populate the graph along the time axis
            rssi.insert(0, {"x": router_time - (i*30), "y": 0})
            sinr.insert(0, {"x": router_time - (i*30), "y": 0})
    except Exception as e:
        log.error('Exception during initializevalues()! exception: {}'.format(e))


# Function to get the RSSI and SINR values from the router. could be condensed a lot.
def getvalues():
    log.debug('Starting getvalues to get current rssi/sinr values')
    global rssi, sinr
    # Get the RSSI
    get_rssi = cs.CSClient().get('/status/wan/devices/%s/diagnostics/DBM/' % primary_connection)
    get_rssi = float(get_rssi['data'])

    # Get the SINR
    get_sinr = cs.CSClient().get('/status/wan/devices/%s/diagnostics/SINR/' % primary_connection)
    # remove first entry in list and append SINR
    get_sinr = float(get_sinr['data'])

    # get the time
    router_time = cs.CSClient().get('/status/system/time/')
    router_time = int(router_time['data'])

    # remove the first entry in rssi and append rssi value to end
    rssi.pop(0)
    rssi.append({"x": router_time, "y": get_rssi})

    # remove the first entry in sinr and append sinr value to end
    sinr.pop(0)
    sinr.append({"x": router_time, "y": get_sinr})


# Function to save the values to json files
def writevalues():
    log.debug('Starting writevalues to write values to json')
    global rssi, sinr
    # save the rssi
    with open('rssi.json', 'w') as f:
        json.dump(rssi, f, indent=4, separators=(',', ': '))
    # save the sinr
    with open('sinr.json', 'w') as f:
        json.dump(sinr, f, indent=4, separators=(',', ': '))
    log.debug('Complete writevalues to write values to json')


def writeJS():
    log.debug('starting writeJS to write values to JS graphs')
    global rssi, sinr
    # save rssi to js
    with open('rssiChart.js', 'w') as f:
        f.write(js_block % (rssi, 'rssi', 'RSSI'))
    with open('sinrChart.js', 'w') as f:
        f.write(js_block % (sinr, 'sinr', 'SINR'))
    log.debug('completed writeJS and wrote values to JS graphs')


# initialize values and write them to the graph
initializevalues()
writevalues()
writeJS()

# Start the main get signal loop!
while True:
    # get primary connection id
    primary_connection = str(cs.CSClient().get('/status/wan/primary_device/')['data'])

    # run our program.

    try:
        log.debug('Starting value get/write loop')
        getvalues()
        writevalues()
        writeJS()
        log.debug('Completed value  get/write loop.  Checking values again in 30 seconds')
        time.sleep(30)

    except Exception as e:
        log.error('Exception during getsignal loop! exception: {}'.format(e))
        log.debug('Error!  Is a modem the primary connection? Checking values again in 30 seconds')
        time.sleep(30)
