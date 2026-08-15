**Philip Koopman, Carnegie Mellon University**

### Best CRCs | CRC Selection | CRC Zoo | Checksum and CRC Blog

**\*\*\* [CRC & Checksum Book](book/index.html) \*\*\*** | [Get software to compute HD lengths for 
yourself.](hdlen.html) | [Pointers to CRC 
Resources](https://betterembsw.blogspot.com/p/crc-resources.html)

These are the "Best" general-purpose CRC polynomials with specific Hamming Distance Properties. 
(See also: [Notation](#notation) and copyright statement). IMPORTANT NOTE: These are "BEST" 
polynomials under an assumption of a low, constant random independent BER such as you'd find in 
communication networks. If you have a BER that is higher than, say, 1 bit in 100,000, or is 
non-constant, or is non-random/non-independent, then you need to understand more before using these 
polynomials.

***This data includes work-in-progress results.***

---

## CRC Summary Tables

Below is a table of CRC Polynomial performance by Hamming Distance. Click a CRC size for detailed 
information about CRC polynomials.

<table><tbody><tr><td rowspan="2">Max length<br>at HD /<br><b>Polynomial</b></td><td colspan="14" 
align="CENTER"><b>CRC Size (bits)</b></td></tr><tr><td align="CENTER"><a 
href="crc3.html"><b>3</b></a></td><td align="CENTER"><a href="crc4.html"><b>4</b></a></td><td 
align="CENTER"><a href="crc5.html"><b>5</b></a></td><td align="CENTER"><a 
href="crc6.html"><b>6</b></a></td><td align="CENTER"><a href="crc7.html"><b>7</b></a></td><td 
align="CENTER"><a href="crc8.html"><b>8</b></a></td><td align="CENTER"><a 
href="crc9.html"><b>9</b></a></td><td align="CENTER"><a href="crc10.html"><b>10</b></a></td><td 
align="CENTER"><a href="crc11.html"><b>11</b></a></td><td align="CENTER"><a 
href="crc12.html"><b>12</b></a></td><td align="CENTER"><a href="crc13.html"><b>13</b></a></td><td 
align="CENTER"><a href="crc14.html"><b>14</b></a></td><td align="CENTER"><a 
href="crc15.html"><b>15</b></a></td><td align="CENTER"><a 
href="crc16.html"><b>16</b></a></td></tr><tr><td><b>HD=2</b></td><td 
align="CENTER"><b>0x5</b></td><td align="CENTER"><b>0x9</b></td><td 
align="CENTER"><b>0x12</b></td><td align="CENTER"><b>0x33</b></td><td 
align="CENTER"><b>0x65</b></td><td align="CENTER"><b>0xe7</b></td><td 
align="CENTER"><b>0x119</b></td><td align="CENTER"><b>0x327</b></td><td 
align="CENTER"><b>0x5db</b></td><td align="CENTER"><b>0x987</b></td><td 
align="CENTER"><b>0x1abf</b></td><td align="CENTER"><b>0x27cf</b></td><td 
align="CENTER"><b>0x4f23</b></td><td align="CENTER"><b>0x8d95</b></td></tr><tr><td><b><a 
href="hd3.html">HD=3</a></b></td><td align="CENTER">4<br><b>0x5</b></td><td 
align="CENTER">11<br><b>0x9</b></td><td align="CENTER">26<br><b>0x12</b></td><td 
align="CENTER">57<br><b>0x33</b></td><td align="CENTER">120<br><b>0x65</b></td><td 
align="CENTER">247<br><b>0xe7</b></td><td align="CENTER">502<br><b>0x119</b></td><td 
align="CENTER">1013<br><b>0x327</b></td><td align="CENTER">2036<br><b>0x5db</b></td><td 
align="CENTER">4083<br><b>0x987</b></td><td align="CENTER">8178<br><b>0x1abf</b></td><td 
align="CENTER">16369<br><b>0x27cf</b></td><td align="CENTER">32752<br><b>0x4f23</b></td><td 
align="CENTER">65519<br><b>0x8d95</b></td></tr><tr><td><b><a 
href="hd4.html">HD=4</a></b></td><td></td><td></td><td align="CENTER">10<br><b>0x15</b></td><td 
align="CENTER">25<br><b>0x23</b></td><td align="CENTER">56<br><b>0x5b</b></td><td 
align="CENTER">119<br><b>0x98</b></td><td align="CENTER">246<br><b>0x17d</b></td><td 
align="CENTER">501<br><b>0x247</b></td><td align="CENTER">1012<br><b>0x583</b></td><td 
align="CENTER">2035<br><b>0x8f3</b></td><td align="CENTER">4082<br><b>0x12e6</b></td><td 
align="CENTER">8177<br><b>0x2322</b></td><td align="CENTER">16368<br><b>0x4306</b></td><td 
align="CENTER">32751<br><b>0xd175</b></td></tr><tr><td><b><a 
href="hd5.html">HD=5</a></b></td><td></td><td></td><td></td><td></td><td 
align="CENTER">4<br><b>0x72</b></td><td align="CENTER">9<br><b>0xeb</b></td><td 
align="CENTER">13<br><b>0x185</b></td><td align="CENTER">21<br><b>0x2b9</b></td><td 
align="CENTER">26<br><b>0x5d7</b></td><td align="CENTER">53<br><b>0xbae</b></td><td 
align="CENTER">52<br><b>0x1e97</b></td><td align="CENTER">113<br><b>0x212d</b></td><td 
align="CENTER">136<br><b>0x6a8d</b></td><td 
align="CENTER">241<br><b>0xac9a</b></td></tr><tr><td><b><a 
href="hd6.html">HD=6</a></b></td><td></td><td></td><td></td><td></td><td></td><td 
align="CENTER">4<br><b>0x9b</b></td><td align="CENTER">8<br><b>0x13c</b></td><td 
align="CENTER">12<br><b>0x28e</b></td><td align="CENTER">22<br><b>0x532</b></td><td 
align="CENTER">27<br><b>0xb41</b></td><td align="CENTER">52<br><b>0x1e97</b></td><td 
align="CENTER">57<br><b>0x372b</b></td><td align="CENTER">114<br><b>0x573a</b></td><td 
align="CENTER">135<br><b>0x9eb2</b></td></tr><tr><td><b>HD=7</b></td><td></td><td></td><td></td><td>
</td><td></td><td></td><td></td><td align="CENTER">5<br><b>0x29b</b></td><td 
align="CENTER">12<br><b>0x571</b></td><td align="CENTER">11<br><b>0xa4f</b></td><td 
align="CENTER">12<br><b>0x12a5</b></td><td align="CENTER">13<br><b>0x28a9</b></td><td 
align="CENTER">16<br><b>0x5bd5</b></td><td 
align="CENTER">19<br><b>0x968b</b></td></tr><tr><td><b>HD=8</b></td><td></td><td></td><td></td><td><
/td><td></td><td></td><td></td><td></td><td align="CENTER">4<br><b>0x4f5</b></td><td 
align="CENTER">11<br><b>0xa4f</b></td><td align="CENTER">11<br><b>0x10b7</b></td><td 
align="CENTER">11<br><b>0x2371</b></td><td align="CENTER">12<br><b>0x630b</b></td><td 
align="CENTER">15<br><b>0x8fdb</b></td></tr><tr><td><b>HD=9</b></td><td></td><td></td><td></td><td><
/td><td></td><td></td><td></td><td></td><td align="CENTER"></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER"></td><td align="CENTER">5<br><b>0x5a47</b></td><td 
align="CENTER">6<br><b>0xe92f</b></td></tr><tr><td><b>HD=10</b></td><td></td><td></td><td></td><td><
/td><td></td><td></td><td></td><td></td><td align="CENTER"></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td><td 
align="CENTER">5<br><b>0xed2f</b></td></tr><tr><td><b>HD=11</b></td><td></td><td></td><td></td><td><
/td><td></td><td></td><td></td><td></td><td align="CENTER"></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td><td 
align="CENTER"></td></tr></tbody></table>

---

<table><tbody><tr><td rowspan="2">Max length<br>at HD /<br><b>Polynomial</b></td><td align="CENTER" 
colspan="8"><b>CRC Size (bits)</b></td></tr><tr><td align="CENTER"><a 
href="crc17.html"><b>17</b></a></td><td align="CENTER"><a href="crc18.html"><b>18</b></a></td><td 
align="CENTER"><a href="crc19.html"><b>19</b></a></td><td align="CENTER"><a 
href="crc20.html"><b>20</b></a></td><td align="CENTER"><a href="crc21.html"><b>21</b></a></td><td 
align="CENTER"><a href="crc22.html"><b>22</b></a></td><td align="CENTER"><a 
href="crc23.html"><b>23</b></a></td><td align="CENTER"><a 
href="crc24.html"><b>24</b></a></td></tr><tr><td><b>HD=2</b></td><td 
align="CENTER"><b>0x16fa7</b></td><td align="CENTER"><b>0x23979</b></td><td 
align="CENTER"><b>0x6fb57</b></td><td align="CENTER"><b>0xb5827</b></td><td 
align="CENTER"><b>0x1707ea</b></td><td align="CENTER"><b>0x308fd3</b></td><td 
align="CENTER"><b>0x540df0</b></td><td align="CENTER"><b>0x8f90e3</b></td></tr><tr><td><b><a 
href="hd3.html">HD=3</a></b></td><td align="CENTER">131054<br><b>0x16fa7</b></td><td 
align="CENTER">262125<br><b>0x23979</b></td><td align="CENTER">524268<br><b>0x6fb57</b></td><td 
align="CENTER">1048555<br><b>0xb5827</b></td><td align="CENTER">2097130<br><b>0x1707ea</b></td><td 
align="CENTER">4194281<br><b>0x308fd3</b></td><td align="CENTER">8388584<br><b>0x540df0</b></td><td 
align="CENTER">16777191<br><b>0x8f90e3</b></td></tr><tr><td><b><a 
href="hd4.html">HD=4</a></b></td><td align="CENTER">65518<br><b>0x1165d</b></td><td 
align="CENTER">131053<br><b>0x25f53</b></td><td align="CENTER">262124<br><b>0x77b0f</b></td><td 
align="CENTER">524267<br><b>0xc1acf</b></td><td align="CENTER">1048554<br><b>0x10df8f</b></td><td 
align="CENTER">2097129<br><b>0x248794</b></td><td align="CENTER">4194280<br><b>0x400154</b></td><td 
align="CENTER">8388583<br><b>0x9945b1</b></td></tr><tr><td><b><a 
href="hd5.html">HD=5</a></b></td><td align="CENTER">240<br><b>0x1724e</b></td><td 
align="CENTER">493<br><b>0x39553</b></td><td align="CENTER">494<br><b>0x5685a</b></td><td 
align="CENTER">1005<br><b>0xc8a89</b></td><td align="CENTER">1004<br><b>0x1edfb7</b></td><td 
align="CENTER">2025<br><b>0x2a952a</b></td><td align="CENTER">2026<br><b>0x6bc0f5</b></td><td 
align="CENTER">4073<br><b>0x98ff8c</b></td></tr><tr><td><b><a href="hd6.html">HD=6</a></b></td><td 
align="CENTER">240<br><b>0x1724e</b></td><td align="CENTER">240<br><b>0x32c69</b></td><td 
align="CENTER">494<br><b>0x5685a</b></td><td align="CENTER">494<br><b>0xe2023</b></td><td 
align="CENTER">1004<br><b>0x1edfb7</b></td><td align="CENTER">1004<br><b>0x395b53</b></td><td 
align="CENTER">2026<br><b>0x6bc0f5</b></td><td 
align="CENTER">2026<br><b>0xbd80de</b></td></tr><tr><td><b>HD=7</b></td><td 
align="CENTER">46<br><b>0x1751b</b></td><td align="CENTER">45<br><b>0x25f6a</b></td><td 
align="CENTER">46<br><b>0x50b49</b></td><td align="CENTER">49<br><b>0x8810e</b></td><td 
align="CENTER">106<br><b>0x12faa5</b></td><td align="CENTER">105<br><b>0x289cfe</b></td><td 
align="CENTER">106<br><b>0x5e2419</b></td><td 
align="CENTER">231<br><b>0x880ee6</b></td></tr><tr><td><b>HD=8</b></td><td 
align="CENTER">22<br><b>0x11bf5</b></td><td align="CENTER">45<br><b>0x25f6a</b></td><td 
align="CENTER">45<br><b>0x779c7</b></td><td align="CENTER">45<br><b>0xd41cf</b></td><td 
align="CENTER">48<br><b>0x198313</b></td><td align="CENTER">105<br><b>0x289cfe</b></td><td 
align="CENTER">105<br><b>0x469d7c</b></td><td 
align="CENTER">105<br><b>0xcba785</b></td></tr><tr><td><b>HD=9</b></td><td 
align="CENTER">8<br><b>0x123bd</b></td><td align="CENTER">11<br><b>0x27bbc</b></td><td 
align="CENTER">13<br><b>0x7573f</b></td><td align="CENTER">21<br><b>0xbe73e</b></td><td 
align="CENTER">20<br><b>0x16e976</b></td><td align="CENTER">22<br><b>0x2aedd3</b></td><td 
align="CENTER">26<br><b>0x53df6e</b></td><td 
align="CENTER">39<br><b>0xed93bb</b></td></tr><tr><td><b>HD=10</b></td><td 
align="CENTER">6<br><b>0x176a7</b></td><td align="CENTER">8<br><b>0x2e7de</b></td><td 
align="CENTER">10<br><b>0x44f75</b></td><td align="CENTER">13<br><b>0xe6233</b></td><td 
align="CENTER">20<br><b>0x16e976</b></td><td align="CENTER">20<br><b>0x247bc4</b></td><td 
align="CENTER">24<br><b>0x463b77</b></td><td 
align="CENTER">26<br><b>0xc7ad89</b></td></tr><tr><td><b>HD=11</b></td><td align="CENTER"></td><td 
align="CENTER">5<br><b>0x26a3d</b></td><td align="CENTER">7<br><b>0x6d133</b></td><td 
align="CENTER">11<br><b>0x8d3cc</b></td><td align="CENTER">10<br><b>0x165751</b></td><td 
align="CENTER">12<br><b>0x36f627</b></td><td align="CENTER">24<br><b>0x463b77</b></td><td 
align="CENTER">23<br><b>0x8cd929</b></td></tr><tr><td><b>HD=12</b></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER">5<br><b>0x51d79</b></td><td 
align="CENTER">7<br><b>0x9d587</b></td><td align="CENTER">10<br><b>0x165751</b></td><td 
align="CENTER">10<br><b>0x22efb7</b></td><td align="CENTER">13<br><b>0x49ad52</b></td><td 
align="CENTER">23<br><b>0x8cd929</b></td></tr><tr><td><b>HD=13</b></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td><td 
align="CENTER">5<br><b>0x25d467</b></td><td align="CENTER">5<br><b>0x4b79d1</b></td><td 
align="CENTER">7<br><b>0xd9588b</b></td></tr><tr><td><b>HD=14</b></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER">5<br><b>0x4b79d1</b></td><td 
align="CENTER">6<br><b>0xb73e91</b></td></tr><tr><td><b>HD=15</b></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td></tr></tbody></table>

---

<table width="50%"><tbody><tr><td rowspan="2">Max length<br>at HD /<br><b>Polynomial</b></td><td 
align="CENTER" colspan="4"><b>CRC Size (bits)</b></td></tr><tr><td align="CENTER"><a 
href="crc25.html"><b>25</b></a></td><td align="CENTER"><a href="crc26.html"><b>26</b></a></td><td 
align="CENTER"><a href="crc27.html"><b>27</b></a></td><td align="CENTER"><a 
href="crc28.html"><b>28</b></a></td></tr><tr><td><b>HD=2</b></td><td 
align="CENTER"><b>0x101690c</b></td><td align="CENTER"><b>0x33c19ef</b></td><td 
align="CENTER"><b>0x5e04635</b></td><td align="CENTER"><b>0x91dc1e3</b></td></tr><tr><td><b><a 
href="hd3.html">HD=3</a></b></td><td align="CENTER">33554406<br><b>0x101690c</b></td><td 
align="CENTER">67108837<br><b>0x33c19ef</b></td><td 
align="CENTER">134217700<br><b>0x5e04635</b></td><td 
align="CENTER">268435427<br><b>0x91dc1e3</b></td></tr><tr><td><b><a 
href="hd4.html">HD=4</a></b></td><td align="CENTER">16777190<br><b>0x10bba2d</b></td><td 
align="CENTER">33554405<br><b>0x278b495</b></td><td 
align="CENTER">67108836<br><b>0x745e8bf</b></td><td 
align="CENTER">134217699<br><b>0xb67b511</b></td></tr><tr><td><b><a 
href="hd5.html">HD=5</a></b></td><td align="CENTER">4072<br><b>0x1b9189d</b></td><td 
align="CENTER">8165<br><b>0x2c45446</b></td><td align="CENTER">8166<br><b>0x6c3ff0d</b></td><td 
align="CENTER">16357<br><b>0x9037604</b></td></tr><tr><td><b><a 
href="hd6.html">HD=6</a></b></td><td align="CENTER">4072<br><b>0x1b9189d</b></td><td 
align="CENTER">4072<br><b>0x2186c30</b></td><td align="CENTER">8166<br><b>0x6c3ff0d</b></td><td 
align="CENTER">8166<br><b>0xd120245</b></td></tr><tr><td><b>HD=7</b></td><td 
align="CENTER">230<br><b>0x136fd31</b></td><td align="CENTER">230<br><b>0x2bd893b</b></td><td 
align="CENTER">484<br><b>0x521f64b</b></td><td 
align="CENTER">483<br><b>0xb9ccb75</b></td></tr><tr><td><b>HD=8</b></td><td 
align="CENTER">230<br><b>0x136fd31</b></td><td align="CENTER">230<br><b>0x2bd893b</b></td><td 
align="CENTER">230<br><b>0x4cb658f</b></td><td 
align="CENTER">483<br><b>0xb9ccb75</b></td></tr><tr><td><b>HD=9</b></td><td 
align="CENTER">40<br><b>0x12b00d4</b></td><td align="CENTER">41<br><b>0x311e9ad</b></td><td 
align="CENTER">48<br><b>0x4429686</b></td><td 
align="CENTER">99<br><b>0xeaa72ab</b></td></tr><tr><td><b>HD=10</b></td><td 
align="CENTER">40<br><b>0x12b00d4</b></td><td align="CENTER">40<br><b>0x32def69</b></td><td 
align="CENTER">41<br><b>0x51aff9a</b></td><td 
align="CENTER">48<br><b>0xacb6aed</b></td></tr><tr><td><b>HD=11</b></td><td 
align="CENTER">24<br><b>0x162054b</b></td><td align="CENTER">24<br><b>0x248d3be</b></td><td 
align="CENTER">36<br><b>0x474fd47</b></td><td 
align="CENTER">35<br><b>0xb094a3e</b></td></tr><tr><td><b>HD=12</b></td><td 
align="CENTER">23<br><b>0x15ed6a9</b></td><td align="CENTER">23<br><b>0x2bfbd8f</b></td><td 
align="CENTER">23<br><b>0x4258c0f</b></td><td 
align="CENTER">35<br><b>0xb094a3e</b></td></tr><tr><td><b>HD=13</b></td><td 
align="CENTER">8<br><b>0x12728bf</b></td><td align="CENTER">9<br><b>0x2d7a067</b></td><td 
align="CENTER">11<br><b>0x6986313</b></td><td 
align="CENTER">15<br><b>0xe9dadcb</b></td></tr><tr><td><b>HD=14</b></td><td 
align="CENTER">7<br><b>0x1291ccf</b></td><td align="CENTER">8<br><b>0x23bb612</b></td><td 
align="CENTER">9<br><b>0x6a611bf</b></td><td 
align="CENTER">11<br><b>0xaf74fc7</b></td></tr><tr><td><b>HD=15</b></td><td align="CENTER"></td><td 
align="CENTER">5<br><b>0x251f66b</b></td><td align="CENTER">7<br><b>0x58695e3</b></td><td 
align="CENTER">8<br><b>0xcf11b95</b></td></tr><tr><td><b>HD=16</b></td><td align="CENTER"></td><td 
align="CENTER">5<br><b>0x251f66b</b></td><td align="CENTER">6<br><b>0x65bd513</b></td><td 
align="CENTER">8<br><b>0xcf11b95</b></td></tr><tr><td><b>HD=17</b></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td></tr></tbody></table>

---

<table width="50%"><tbody><tr><td rowspan="2">Max length<br>at HD /<br><b>Polynomial</b></td><td 
align="CENTER" colspan="4"><b>CRC Size (bits)</b></td></tr><tr><td align="CENTER"><a 
href="crc29.html"><b>29</b></a></td><td align="CENTER"><a href="crc30.html"><b>30</b></a></td><td 
align="CENTER"><a href="crc31.html"><b>31</b></a></td><td align="CENTER"><a 
href="crc32.html"><b>32</b></a></td></tr><tr><td><b>HD=2</b></td><td 
align="CENTER"><b>0x16dfbf51</b></td><td align="CENTER"><b>0x31342a2f</b></td><td 
align="CENTER"><b>0x737e312b</b></td><td align="CENTER"><b>0xad0424f3</b></td></tr><tr><td><b><a 
href="hd3.html">HD=3</a></b></td><td align="CENTER">536870882<br><b>0x16dfbf51</b></td><td 
align="CENTER">1073741793<br><b>0x31342a2f</b></td><td 
align="CENTER">2147483616<br><b>0x737e312b</b></td><td 
align="CENTER">4294967263<br><b>0xad0424f3</b></td></tr><tr><td><b><a 
href="hd4.html">HD=4</a></b></td><td align="CENTER">268435426<br><b>0x11c4dfb5</b></td><td 
align="CENTER">536870881<br><b>0x2254329d</b></td><td 
align="CENTER">1073741792<br><b>0x52aa4332</b></td><td 
align="CENTER">2147483615<br><b>0xc9d204f5</b></td></tr><tr><td><b><a 
href="hd5.html">HD=5</a></b></td><td align="CENTER">16356<br><b>0x1cf492f3</b></td><td 
align="CENTER">32737<br><b>0x2adf3aaf</b></td><td align="CENTER">32738<br><b>0x74f9e7cb</b></td><td 
align="CENTER">65505<br><b>0xd419cc15</b> (**)</td></tr><tr><td><b><a 
href="hd6.html">HD=6</a></b></td><td align="CENTER">16356<br><b>0x1cf492f3</b></td><td 
align="CENTER">16356<br><b>0x2ad4a56a</b></td><td align="CENTER">32738<br><b>0x74f9e7cb</b></td><td 
align="CENTER">32738<br><b>0x9960034c</b> (**)</td></tr><tr><td><b>HD=7</b></td><td 
align="CENTER">484<br><b>0x12e8b5b6</b></td><td align="CENTER">993<br><b>0x2a9b3e15</b></td><td 
align="CENTER">992<br><b>0x60f2920b</b></td><td align="CENTER">992<br><b>0xf8c9140a</b> 
(**)</td></tr><tr><td><b>HD=8</b></td><td align="CENTER">483<br><b>0x13a46755</b></td><td 
align="CENTER">483<br><b>0x2017ed6a</b></td><td align="CENTER">992<br><b>0x60f2920b</b></td><td 
align="CENTER">992<br><b>0xf8c9140a</b></td></tr><tr><td><b>HD=9</b></td><td 
align="CENTER">100<br><b>0x1e150a87</b></td><td align="CENTER">100<br><b>0x242c0684</b></td><td 
align="CENTER">100<br><b>0x6c740b8d</b></td><td 
align="CENTER">223<br><b>0x9d7f97d6</b></td></tr><tr><td><b>HD=10</b></td><td 
align="CENTER">100<br><b>0x1e150a87</b></td><td align="CENTER">100<br><b>0x242c0684</b></td><td 
align="CENTER">100<br><b>0x6c740b8d</b></td><td 
align="CENTER">100<br><b>0xb49c1c96</b></td></tr><tr><td><b>HD=11</b></td><td 
align="CENTER">35<br><b>0x1c27bd8b</b></td><td align="CENTER">36<br><b>0x34c8e00d</b></td><td 
align="CENTER">36<br><b>0x456a3501</b></td><td 
align="CENTER">38<br><b>0x85b9561d</b></td></tr><tr><td><b>HD=12</b></td><td 
align="CENTER">35<br><b>0x1c27bd8b</b></td><td align="CENTER">35<br><b>0x2468c69c</b></td><td 
align="CENTER">35<br><b>0x6bee283f</b></td><td 
align="CENTER">36<br><b>0x950ebfae</b></td></tr><tr><td><b>HD=13</b></td><td 
align="CENTER">14<br><b>0x13a6f65c</b></td><td align="CENTER">16<br><b>0x2b967ef9</b></td><td 
align="CENTER">18<br><b>0x6624b2eb</b></td><td 
align="CENTER">20<br><b>0x93b39b1b</b></td></tr><tr><td><b>HD=14</b></td><td 
align="CENTER">14<br><b>0x13a6f65c</b></td><td align="CENTER">14<br><b>0x3c9a0b27</b></td><td 
align="CENTER">16<br><b>0x47e62564</b></td><td 
align="CENTER">19<br><b>0xa094afb5</b></td></tr><tr><td><b>HD=15</b></td><td 
align="CENTER">9<br><b>0x12ff393a</b></td><td align="CENTER">11<br><b>0x290d6d0e</b></td><td 
align="CENTER">12<br><b>0x52d246e1</b></td><td 
align="CENTER">15<br><b>0xa2572962</b></td></tr><tr><td><b>HD=16</b></td><td 
align="CENTER">8<br><b>0x15e165a6</b></td><td align="CENTER">9<br><b>0x23136e56</b></td><td 
align="CENTER">11<br><b>0x6d094c5d</b></td><td 
align="CENTER">13<br><b>0xe89061db</b></td></tr><tr><td><b>HD=17</b></td><td 
align="CENTER"></td><td align="CENTER">4<br><b>0x229df1ac</b></td><td 
align="CENTER">5<br><b>0x47d2d9ab</b></td><td 
align="CENTER">7<br><b>0xa86be4db</b></td></tr><tr><td><b>HD=18</b></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER">4<br><b>0x46e56a7c</b></td><td 
align="CENTER">5<br><b>0x973afb51</b></td></tr><tr><td><b>HD=19</b></td><td align="CENTER"></td><td 
align="CENTER"></td><td align="CENTER"></td><td align="CENTER"></td></tr></tbody></table>

**(\*\*)** means that this is a temporary result which has approximately the longest possible 
dataword length at the specified HD, but might not be the "best" possible value. (For example, 
probably there is some as yet unknown result with a slightly longer dataword length at that HD or 
with lower weights at the same HD.) Ongoing computations will be used to update this value to the 
"best" value when available. In the meantime, there's nothing wrong with using this polynomial as 
long as it provides adequate properties for your application.

## Additional polynomials (33-64 bits; Special Properties)

- For details about these polynomials, and for CRCs larger than 32 bits, see the [CRC 
Zoo](crc64.html)
- For specialized polynomials, see the [CRC Selection page](details.html). This includes 
polynomials with combination properties and good polynomials with all zero terms after the lowest 
byte.

---

To use these tables: top number in each cell is maximum dataword length at that Hamming Distance. 
The bottom number in each cell is a "good" polynomial that gives at least that HD up to the 
indicated dataword length in implicit +1 notation. For example, the polynomial 0x247 is a 10-bit 
CRC that provides HD=4 (or better) up to 501 bit dataword length (501+10=511 bit codeword length). 
The corresponding polynomial is: 0x247=x^10 +x^7 +x^3 +x^2 +x +1, and is alternately known as 0x48f 
in explicit +1 notation. See the [Polynomial Zoo](hw_data.html) for detailed information (or click 
the CRC size link at the top of each column). Additionally, see the tables below for more nuanced 
selection criteria.

*Notes: **Minimum dataword length evaluated for the above table is 4 bits.** Grayed-out boxes mean 
that it has been confirmed that the HD at that row cannot be achived with a dataword length of 4 
bits or longer. Color highlighted cells indicated work in progress/missing data.*

---

## Notation:

- For details on interpreting the data rows and data file formats, see [Hamming Weight Data notes 
section](notes.html).
- \*p - primitive polynomial. This has optimal length for HD=3, and good HD=2 performance above 
that length.
- \*o - odd bit errors detected. This has a factor of (x+1) and detects all odd bit errors 
(implying that even number of bit errors have an elevated undetected error rate)
- \*op - odd bit errors detected plus primitive. This is a primitive polynomial times (x+1). It has 
optimal length for HD=4, and detects all odd bit errors.
- \*\* - HD confirmed, but minimum weight selection at maximum length has been approximated due to 
long run-time. In other words, this polynomial will perform as advertised, but there is a slight 
chance a slightly better polynomial exists that was not found due to less than an exhaustive 
search. This only applies to a few 32-bit and larger polynomials.

---

This web page and all data files are Copyrighted 2015-2018 by Philip Koopman, Carnegie Mellon 
University.

This work is licensed under a [Creative Commons Attribution 4.0 International 
License](http://creativecommons.org/licenses/by/4.0/).

Please note that if any data errors or other issues are identified they will be updated at this 
page, but not necessarily anywhere that has copied these results. Therefore, you should always 
confirm at this URL: 
[http://users.ece.cmu.edu/~koopman/crc/](http://users.ece.cmu.edu/~koopman/crc/) that you have the 
most current version of data before using it.
