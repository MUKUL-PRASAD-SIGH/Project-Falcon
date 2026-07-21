const catalyst = require('zcatalyst-sdk-node');

module.exports = (context, basicIO) => {
    const app = catalyst.initialize(context);
    const reqBody = basicIO.getArgument('reqBody') || {};
    
    // Karnataka Bounding Box
    const MIN_LAT = 11.5;
    const MAX_LAT = 18.5;
    const MIN_LON = 74.0;
    const MAX_LON = 78.5;
    
    const lat = parseFloat(reqBody.latitude);
    const lon = parseFloat(reqBody.longitude);
    
    if (isNaN(lat) || isNaN(lon)) {
        basicIO.write(JSON.stringify({
            status: "error",
            message: "Invalid GPS coordinates: Not a number."
        }));
        context.close();
        return;
    }
    
    if (lat >= MIN_LAT && lat <= MAX_LAT && lon >= MIN_LON && lon <= MAX_LON) {
        basicIO.write(JSON.stringify({
            status: "success",
            message: "GPS coordinates are within Karnataka bounding box."
        }));
    } else {
        basicIO.write(JSON.stringify({
            status: "error",
            message: "GPS coordinates out of bounds."
        }));
    }
    
    context.close();
};
