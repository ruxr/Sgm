#!/bin/sh
#
DIR=/var/www/pub/Sgm
CFG=$DIR.cfg
#
LANG=C
E=
Q=$QUERY_STRING
case $Q in *[!a-zA-Z0-9_-]*|""|-*) E="Illegal CGI query!";; esac
[ -z "$E" ] && F=$DIR/$Q.sgm && [ -f "$F" ] || E=${E:-"Missing monitoring history file $Q.sgm!"} F=/dev/null
[ -f "$CFG" ] || E=${E:-"Missing configuration file ${CFG##*/}!"}
awk -vE="$E" -vD="$CFG" -vQ="$Q" '
/^((-?[1-9][0-9]*)|0?) ((-?[1-9][0-9]*)|0?)$/ {
	if(NR > 2 && NR < 1603) { F[NR] = $1; L[NR] = $2; next }
}
/^[1-9][0-9]*(( -?[1-9][0-9]*)|( 0?)){2}$/ {
	if(NR == 1) {
		s = $0; tn = $1; fn = $2; ln = $3; next
	}
	if(NR == 2 && $1 <= tn && $2 != "" && ($0 == s || s == (tn "  "))) {
		tl = $1; fl = $2; ll = $3; next
	}
}
{ exit }
function Htm(s) {
	gsub(/&/, "\\&amp;", s)
	gsub(/</, "\\&lt;", s)
	gsub(/>/, "\\&gt;", s)
	return s
}
function Num(i, j) {
	if(i == "") return "Unknown"
	if(Rate) { i /= Rate; j /= Rate }
	if(j) {
		if(j ~ /\./ && i) i = sprintf("%.1f", i)
		else {
			for(j = 1; sub(/000$/, "", i);) j++
			if(--j) return i " " R[j]
		}
		return i
	}
	for(; i > 9999; j++) i /= 1000
	if(i ~ /\./) i = sprintf("%." Prec "f", i)
	if(j || Short != "") return i " " R[j] Short
	return i

}
function Txt(t, x, y) { return "<text x=\"" x "\" y=\"" y "\">" t "</text>" }
function Way(s, d) { return "<path style=\"" s "\" d=\"" d "\"/>" }
function Two() { gsub(/v2/, "v-102.5", p); gsub(/v-2/, "v102.5", p); return p }
function Fig(D, s, l) {
	if(base) for(i = end; i <= iu; i++) if(D[i]) D[i] -= base
	p = "M99," go - (y = int((D[i = end]) / scale)) " l"
	while(i++ < iu) p = p " 1," (y - (y = int((D[i]) / scale)))
	print Way(s, p l)
}
function Row(n, D, c, t) {
	s = x = y = D[i = iu]
	if(s == "") j = 0; else j = 1
	while(--i > end)
		if(D[i] != "") {
			s += D[i]; j++;
			if(x == "" || x < D[i]) x = D[i]
			if(y == "" || y > D[i]) y = D[i]
		}
	if(max == "" || max < x) max = x
	if(min == "" || min > y) min = y
	if(j) s /= j
	return "<tr><td style=\"text-align:left;color:" c "\">" t \
		"<td>" Num(x) "<td>" Num(s) "<td>" Num(y) "<td>" Num(D[iu])
}
function Dat(x, i) {
	p = "M" (x = 498 - int(x)) (j = ",6 v108")
	if((x -= i) > 98) p = p " M" x j
	print Way("stroke:red", p)
	scale = qr / 25
	end++
	if(Fill != "") Fig(F, sw "stroke:#00f000;fill:#00f000", " L498," go " L99," go " z")
	if(Line != "") Fig(L, "stroke:blue;fill:none")
	print "</svg>\n<table width=\"100%\">\n<tr><th><th>Max<th>Mid<th>Min<th>Now"
	if(Fill != "") print f
	if(Line != "") print l
	print "</table>"
}
function New(i, s, t) {
	print "<hr>\n<p><b>" s " graph</b> (" t " average)</p>\n" \
		"<svg width=\"512\" height=\"128\" style=\"font-size:70%;text-anchor:middle\">\n" \
		"<text transform=\"translate(20,64) rotate(270)\">" Desc "</text>\n" \
		Way(sb, "M98,0.5 v115") "\n" \
		Way(sb sw, "M95,6 l3,-6 3,6") "\n" \
		Way(sb, "M96,10 h2 M96,35 h2 M96,60 h2 M96,85 h2 M96,110 h2") "\n" \
		Way(sg, "M99,10 h402 M99,35 h402 M99,60 h402 M99,85 h402 M99,110 h402")
	end = (iu = i) - 400
	max = min = ""
	if(Fill != "") f = Row(n, F, "green", Fill)
	if(Line != "") l = Row(n, L, "blue", Line)
	if(max == "") max = min = 0
	if(max < 0) { ne = -1; go = 10; bar = -min }
	else if(min >= 0) { ne = 1; go = 110; bar = max }
	else {
		Crop = ne = 0; go = 60
		if((bar = max + min) < 0) bar = -bar
		bar = int((bar + 2) / 3 * 4)
	}
	if(Crop && max != min) {
		for(i = max - min; i < 4; i++) if(bar - i < 1) break
		base = (bar - (bar = i)) * ne
	} else base = 0
	if(!bar) qr = 1
	else if(bar < 1000) qr = int((bar + 3) / 4)
	else qr = int(((((y = bar - 1) + (i = 10^(length(y) - 3))) / i) + 3) / 4) * i
	i = base
	if(ne > 0) i -= qr
	else if(ne < 0) i -= qr * 5
	else if(qr > max) { i -= qr * 4; go -= 25 }
	else if(qr > -min) { i -= qr * 2; go += 25 }
	else i -= qr * 3
	y = 138
	print "<g style=\"text-anchor:end\">"
	while((y -= 25) > 0) print Txt(Num(i += qr, qr), 90, y)
	print "</g>\n" Way(sb, "M93," go " h418.5") "\n" Way(sb sw, "M506," go - 3 " l6,3 -6,3")
}
function End() {
	if(E) Err(E)
	else if(Note) print "<hr>\n" Note
	print "<hr>\n<p style=\"text-align:right;font:italic 70% small-caption\">" \
		"@(#) Sgm.cgi V2.0 (C) 2022 by Roman Oreshnikov</p>\n</body>\n</html>"
	exit
}
function Err(s) { print "<p style=\"color:red\">" s "</p>" }
END {
	if(!E && NR != 1602) E = "Error in monitorig history file " Q ".sgm!"
	Title = "Sgm.cgi"
	if(!E) {
		H["Desc"] = "Bytes per Second"
		H["Fill"] = "Input"
		H["Graph"] = "dwmy"
		H["Line"] = "Output"
		H["Prec"] = 1
		H["Range"] = "kMGT"
		H["Short"] = "B/s"
		while(getline < D)
			if(match($0, /^([A-Z][a-z]+)(\[([a-zA-Z0-9_-]+)\])?\s*=\s*(.*)$/, a)) {
				if(a[3] == Q) f++
				else if(f) break
				else if(a[3] != "" || a[1] == "Title") continue
				H[n = a[1]] = a[4]
			} else if($0 ~ /^\s/ && n != "") {
				sub(/^\s+/, "")
				H[n] = H[n] "\n" $0
			} else n = ""
		if((f = Htm(H["Title"])) != "") Title = f
		else E = "Missing value for Title[" Q "] in configuration file Sgm.cfg!"
		Crop = H["Crop"]
		Desc = Htm(H["Desc"])
		Fill = Htm(H["Fill"])
		Graph = H["Graph"]
		Intro = H["Intro"]
		Note = H["Note"]
		Line = Htm(H["Line"])
		Prec = int(H["Prec"])
		Range = H["Range"]
		Rate = int(H["Rate"])
		Short = Htm(H["Short"])
	}
	print	"Content-Type: text/html; charset=utf-8\n\n" \
		"<!DOCTYPE html>\n<html>\n<head>\n" \
		"<meta http-equiv=\"Content-Type\"",
			"content=\"text/html; charset=utf-8\">\n" \
		"<meta http-equiv=\"Pragma\" content=\"no-cache\">\n" \
		"<meta http-equiv=\"Refresh\" content=\"300\">\n" \
		"<title>" Title "</title>\n<style>\n" \
		"tr td { text-align:right }\ntd, th { padding-left:1ex }\n" \
		"p { text-indent:2em }\n</style>\n</head>\n" \
		"<body style=\"max-width:512px\">\n" \
		"<h3 align=\"center\">" Title "</h3>"
	if(E) End()
	ts = strftime("%c", tl)
	if(fn == "") Err("Error getting monitoring data: <b>" strftime("%c", tn) \
			"</b></p>\n<p>Last successful data acquisition: <b>" ts "</b>")
	else print "<p>Latest statistics update: <b>" ts "</b></p>"
	if(Intro) print "<hr>\n" Intro
	tz = int((tz = strftime("%z", tn)) / 100) * 3600 + tz % 100 * 60
	tz += tn
	sb = "stroke:black;"
	sw = "stroke-width:0.5;"
	sg = sb sw "stroke-dasharray:0.5 1.5"
	split(Range, R, "")
	if(Graph ~ /d/) {
		New(1602, "Daily", "5 minute")
		p = "M" (x = 498 - int(tz % 3600 / 300)) ",110 v" (i = 2)
		for(t = strftime("%H", tn); (x -= 12) > 98;) {
			p = p " m-12,0 v" (i = -i)
			if(--t < 0) t += 24
			if(i < 0) print Txt(t, x, 125)
		}
		print Way(sb, p) "\n" Way(sg, Two())
		Dat(tz % 86400 / 300, 288)
	}
	if(Graph ~ /w/) {
		New(1202, "Weekly", "30 minute")
		p = "M" (x = 498 - int(tz % 86400 / 1800)) ",110 v" (i = 2)
		for(t = tn; (x -= 48) > 98; p = p " m-48,0 v" (i = -i))
			print Txt(strftime("%a", t -= 86400), x + 24, 125)
		print Way(sb, p) "\n" Way(sg, Two())
		Dat((tz + 259200) % 604800 / 1800, 336)
	}
	if(Graph ~ /m/) {
		New(802, "Monthly", "2 hour")
		p = "M" (x = 498 - int(tz % 86400 / 7200)) ",110 v" (n = i = 2)
		for(t = tn - 86400; (x -= 12) > 100; p = p " m-12,0 v" (i = -i))
			if(i > 0) {
				if((n -= 2) < 1) n = int(strftime("%d", t))
				print Txt(n, x + 6, 125)
				t -= 172800
			}
		print Way(sb, p)
		p = "M" (x = 498 - int((tz + 259200) % 604800 / 7200)) ",110 v" (i = -101)
		while((x -= 84) > 98) p = p " m-84,0 v" (i = -i)
		print Way(sg, p)
		Dat(((n = strftime("%d", tn)) - 1) * 12 + tz % 86400 / 7200,
			strftime("%d", tn - n * 86400) * 12)
	}
	if(Graph ~ /y/) {
		New(402, "Yearly", "1 day")
		x = 498 - (n = strftime("%d", t = tn - 86400))
		p = "M" x ",110 v" (i = 2)
		while((x -= (n = strftime("%d", t -= n * 86400))) > 98) {
			p = p " m-" n ",0 v" (i = -i)
			print Txt(strftime("%b", t), x + int(n / 2), 125)
		}
		print Way(sb, p) "\n" Way(sg, Two())
		Dat(i = strftime("%j", tn - 86400), strftime("%j", tn - ++i * 86400))
	}
	End()
}' "$F"
