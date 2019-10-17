function b(a, b) {
  var c, d;
  for (c = 0; c < b.length - 2; c += 3)
    (d = b.charAt(c + 2)),
      (d = d >= "a" ? d.charCodeAt(0) - 87 : Number(d)),
      (d = "+" == b.charAt(c + 1) ? a >>> d : a << d),
      (a = "+" == b.charAt(c) ? 4294967295 & (a + d) : a ^ d);
  return a;
}
function tk(a, c) {
  var d, e, f, g, h, i;
  for (
    d = c.split("."), e = Number(d[0]) || 0, f = [], g = 0, h = 0;
    h < a.length;
    h++
  )
    (i = a.charCodeAt(h)),
      128 > i
        ? (f[g++] = i)
        : (2048 > i
            ? (f[g++] = 192 | (i >> 6))
            : (55296 == (64512 & i) &&
              h + 1 < a.length &&
              56320 == (64512 & a.charCodeAt(h + 1))
                ? ((i =
                    65536 + ((1023 & i) << 10) + (1023 & a.charCodeAt(++h))),
                  (f[g++] = 240 | (i >> 18)),
                  (f[g++] = 128 | (63 & (i >> 12))))
                : (f[g++] = 224 | (i >> 12)),
              (f[g++] = 128 | (63 & (i >> 6)))),
          (f[g++] = 128 | (63 & i)));
  for (a = e, g = 0; g < f.length; g++) (a += f[g]), (a = b(a, "+-a^+6"));
  return (
    (a = b(a, "+-3^+b+-f")),
    (a ^= Number(d[1]) || 0),
    0 > a && (a = (2147483647 & a) + 2147483648),
    (a %= 1e6),
    a.toString() + (a ^ e)
  );
}
window.seccode = 8511813095152;
