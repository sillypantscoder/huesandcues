function coordsToAngle(x, y) { return Math.atan2(y, x) * 180 / Math.PI; }
Math.dist = (p1, p2) => Math.sqrt(((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2))
function getColorWheelPointColor(x, y) {
	var ypc = y / 480
	var xpc = x / 800
	xpc = (xpc - 0.5) * 2
	ypc = (ypc - 0.5) * 2
	var angle = coordsToAngle(xpc, ypc) + 90
	if (angle < 0) angle += 360
	// Get the value
	var val = 50
	var dist = Math.dist([400, 240], [x, y])
	if (dist < 200) {
		var pc = dist / 266
		val += (1 - pc) * 50
	}
	return `hsl(${angle}deg, 100%, ${val}%)`
}
function getOffset(elm) {
	var rect = elm.getBoundingClientRect()
	return rect.top
}