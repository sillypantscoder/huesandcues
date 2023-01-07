(() => {
	var x = new XMLHttpRequest()
	x.open("GET", "/getscore?name=" + location.search.substr(6))
	x.addEventListener("loadend", (v) => {
		var e = document.createElement("aside")
		e.setAttribute("style", "position: absolute; left: 0; bottom: 0; padding: 1em; margin: 1em; margin-bottom: 0; border: 1px solid black; border-bottom: 0; border-top-left-radius: 1em; border-top-right-radius: 1em; pointer-events: none;")
		e.innerText = "Your score: " + v.target.responseText
		document.body.appendChild(e)
	})
	x.send()
})()