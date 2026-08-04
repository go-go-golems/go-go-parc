---
title: "Captured source: External Http Api"
source_file: "external-http-api.md"
type: source
---

# Captured source: External Http Api

Original ticket source file: `external-http-api.md`.

the open http api lets you fully control busy bar using your own scripts, applications, or services in any programming
language the http api is available over usb, wi fi, and the internet on this page, you'll learn about the http api
capabilities docid\\ h4whpextnlyjsr9plxsar authentication docid\\ h4whpextnlyjsr9plxsar http api reference docid\\
h4whpextnlyjsr9plxsar busylib libraries docid\\ h4whpextnlyjsr9plxsar capabilities timer control — control the busy
and custom modes display control — render text and images on both displays, adjust brightness audio control —
upload and play audio files, adjust volume real time updates — get display frames and device state changes over
websocket input simulation — emulate button presses and scroll wheel events file management — upload, organize, and
delete files stored on the device firmware updates — update firmware from a local file or over the internet wi fi and
bluetooth — scan and connect the device to wi fi networks, enable ble advertising, remove ble pairings, and check
connection status busy account — link or unlink the device with your busy account, get account info matter
integration — connect the device to your smart home system config — set the device name, system time, time zone,
and more system info — get device status, power, and firmware details how it works http api follows a client server
architecture the busy bar acts as an http server, waiting for incoming requests, while an http client sends requests to
the device the http client can be any application capable of sending http requests, such as a smart home system, a
script, a desktop or mobile application, or even a web browser for the simplest test, connect busy bar to your computer
via usb and enter 10 0 4 20/api/status/firmware the browser will send an http request to busy bar and display its
response an http request url consists of base url, which depends on how busy bar is connected endpoint, which
identifies the type of request to busy bar all available endpoints are listed in the http api reference base url the
base url for http api requests depends on how your busy bar is connected via usb use http //10 0 4 20/api http //10 0 4
20/api as the base url via wi fi (lan) use the ip address assigned by your wi fi router, for example, xx xx xx xx/api
to view the current ip address on your busy bar, go to settings → wi fi → \\\[your wi fi ap name\] → view ip
address via internet use https //api busy app/busybar https //api busy app/busybar as the base url connecting via wi fi
(lan) or the internet requires authentication for details, see the authentication docid\\ h4whpextnlyjsr9plxsar section
below wi fi access \\<font color="#2b7eff"> ou need to enable wi fi access \\</font> wi fi (lan) connections to busy
bar are \\<font color="#475f85"> disabled by default for security reasons \\</font> this applies to both the local web
interface and the http api to enable wi fi access to busy bar connect your busy bar to a computer via usb open the busy
bar local web interface in a web browser http //10 0 4 20/ http //10 0 4 20/ on the network page, in the http api
section, turn on the http api access toggle click set password and enable, and set a password from now on, busy bar
will ask for this password every time you log in to the web interface via wi fi you'll also need to include this
password in all http requests for authentication authentication authentication is how the device verifies that an
incoming http api request was actually sent by its owner or someone the owner trusts without authentication, busy bar
returns a 403 forbidden error in response to the request the authentication method depends on how you connect to busy
bar via usb, wi fi, or the internet via usb a usb connection is considered a secure communication channel, so
authentication is not used over usb you can send any http api requests to the device at its ip address 10 0 4 20
without authentication via wi fi http api requests over wi fi (lan) are authenticated using a password that is
configured in the local web interface when wi fi access is enabled learn more about enabling wi fi access in the wi fi
access docid\\ h4whpextnlyjsr9plxsar section every http request sent to the device via wi fi must include this password
in the x api token header see examples below curl x get \\\\ "http //\\\[busy bar ip address\]/api/status" \\\\ h
"accept application/json" \\\\ h 'x api token \\<your password>'const response = await fetch("http //\\\[busy bar ip
address\]/api/status", { headers { "accept" "application/json", "x api token" \\<your password>, }, }); import requests
response = requests get( "http //\\\[busy bar ip address\]/api/status", headers={ "accept" "application/json", "x api
token" \\<your password>, }, ) via internet internet authentication is performed using an api token, which is generated
in your busy account after you connect your busy bar to the account learn more about managing api tokens docid
3auwybgy9fgu b8dnfm4h every http request sent to the device must include this api token in the authorization header
using the bearer authentication scheme see examples below curl x get \\\\ "https //api busy app/busybar/status" \\\\ h
"accept application/json" \\\\ h "authorization bearer \\<your api token>"const response = await fetch("https //api
busy app/busybar/status", { headers { "accept" "application/json", "authorization" "bearer \\<your api token>", }, });
import requests response = requests get( "https //api busy app/busybar/status", headers={ "accept" "application/json",
"authorization" "bearer \\<your api token>", }, ) http api reference http api reference https //api busy
app/busybar/docs is an interactive page where you can browse all http api endpoints — view all supported api requests
view the api schemas that describe the json objects used by the http api download the openapi yml file, which contains
the http api specification in the openapi format test any api request expand the desired endpoint, click try it out,
edit the request parameters or body if necessary, and then click execute how to open the http api reference you can
open the http api reference in one of two ways \\<font color="#ed0018">option 1 \\</font> from the busy bar local web
interface open the following url in your web browser http //10 0 4 20/docs (when connected over usb) http //\\<busy bar
ip address>/docs (when connected over wi fi) alternatively, open the network tab in the local web interface and, in the
http api section, click either over usb or over wi fi this opens the http api reference hosted directly on the device
it documents the version of the http api implemented in the device's firmware when you test api requests from the
reference page, they are sent directly to the busy bar over wi fi or usb \\<font color="#ed0018">option 2 \\</font>
public http api reference open the following url in your web browser https //api busy app/busybar/docs https //api busy
app/busybar/docs in the page header, you can select the busy bar firmware version whose http api reference you want to
view when you test api requests from the public reference page, the requests are sent to your busy bar over the
internet through our cloud service try the api from the http api reference you can send requests to your busy bar right
from the http api reference in the example below, you'll show text on the front screen and an image on the back screen
\\<font color="#ed0018"> step 1 \\</font> authenticate, if needed to try api requests, you may need to authenticate
first, depending on how you access the http api reference over usb ( http //10 0 4 20/docs ) — no authentication
needed, just send requests over wi fi ( http //\\<busy bar ip address>/docs ) — click authorize and enter the
password you set when enabling wi fi access /#wi fi access over the internet ( api busy app/busybar/docs ) — click
authorize and enter an api token docid 3auwybgy9fgu b8dnfm4h generated in your busy account \\<font
color="#ed0018">step 2 \\</font> upload an image for the back screen \\<font color="#2b7eff"> or the back screen, you
need a 160x80 px png image \\</font> you can download our example image by clicking here https //cdn flipperzero
one/hello example png try the endpoint that uploads an image in the assets group, expand \\<font color="#22c55e"> post
\\</font> api/assets/upload and click try it out in the request body, click choose file and select your file click
execute to upload the file to your busy bar the image is now in your busy bar's memory to show it, continue to step 3
\\<font color="#ed0018">step 3 \\</font> show text and an image on the busy bar screens scroll down to the \\<font
color="#22c55e"> post \\</font> /busybar/display/draw endpoint expand the endpoint and click try it out (optional) edit
the request body for example, change the text parameter to show a different text click execute your busy bar shows the
text on the front screen and the uploaded image on the back screen busylib libraries busylib is the official open
source library for building applications that interact with busy bar it provides ready to use python and typescript
apis that abstract the underlying http api advantages simplifies development by handling http request construction and
response processing developers can work with a simple, high level api without worrying about the underlying http
protocol implements websocket communication for receiving real time events from the device and for screen streaming
supports both synchronous and asynchronous interaction with busy bar, making it suitable for both simple applications
and concurrent workflows get busylib we maintain busylib for python and typescript typescript library https //go busy
app/typescript library python library https //pypi org/project/busylib/ \\<font color="#2b7eff"> community net library
\\</font> there's also a net client for the busy bar http api, built and maintained by the community busybar net https
//busybar dotnet homotechsual dev/
